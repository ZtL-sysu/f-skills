import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
AUTO = SKILL / "scripts" / "auto_merge.py"
CHECKPOINT = SKILL / "scripts" / "checkpoint_manifest.py"
PY = sys.executable
BASE = Path(tempfile.mkdtemp(prefix="auto-merge-test-")).resolve()


def run(*args, cwd=None, ok=True):
    proc = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", capture_output=True)
    assert (proc.returncode == 0) == ok, (args, proc.returncode, proc.stdout, proc.stderr)
    return proc


def git(repo, *args, ok=True):
    return run("git", "-C", str(repo), *args, ok=ok)


def fixture():
    token = uuid.uuid4().hex[:8]
    remote = BASE / ("remote-" + token)
    main_repo = BASE / ("main-" + token)
    agent_repo = BASE / ("agent-" + token)
    run("git", "init", "-q", "--bare", str(remote))
    for repo in (main_repo, agent_repo):
        run("git", "clone", "-q", str(remote), str(repo))
        git(repo, "config", "user.name", "Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
    (main_repo / "protocol.md").write_text("Frozen protocol\n")
    (main_repo / "base.txt").write_text("line one\nline two\n")
    git(main_repo, "add", "protocol.md", "base.txt")
    git(main_repo, "commit", "-qm", "base")
    git(main_repo, "branch", "-M", "main")
    git(main_repo, "push", "-q", "-u", "origin", "main")
    git(agent_repo, "fetch", "-q", "origin")
    git(agent_repo, "checkout", "-q", "-b", "agent/e0/a1", "origin/main")
    return remote, main_repo, agent_repo


def commit_all(repo, message):
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)


def judge(repo, *extra):
    proc = subprocess.run(
        [PY, "-X", "utf8", str(AUTO), "--repo", str(repo),
         "--branch", "HEAD", "--remote", "origin", "--target", "main", *extra],
        text=True, encoding="utf-8", capture_output=True,
    )
    return json.loads(proc.stdout.strip())


def remote_main(repo):
    return git(repo, "ls-remote", "origin", "refs/heads/main").stdout.split()[0]


# 1. pure new file: allowed, dry run changes nothing, --execute merges and pushes
remote, main_repo, agent = fixture()
head_before = remote_main(agent)
(agent / "new.txt").write_text("brand new\n")
commit_all(agent, "add new artifact")
doc = judge(agent)
assert doc["status"] == "allowed" and doc["executed"] is False, doc
assert doc["files_added"] == 1 and doc["lines_deleted"] == 0, doc
assert remote_main(agent) == head_before, "dry run must not push"
doc = judge(agent, "--execute")
assert doc["status"] == "merged" and doc["merge_commit"], doc
assert doc["merge_commit"] != doc["target_head"], "merge must create a new commit"
assert remote_main(agent) == doc["merge_commit"], doc
git(main_repo, "fetch", "-q", "origin", "main")
assert git(main_repo, "show", "FETCH_HEAD:new.txt").stdout == "brand new\n"

# 2. append-only modification of an existing file is additive
remote, main_repo, agent = fixture()
with (agent / "base.txt").open("a") as stream:
    stream.write("line three\n")
commit_all(agent, "append log")
doc = judge(agent)
assert doc["status"] == "allowed" and doc["files_appended"] == 1, doc

# 3. rewriting an existing line is refused
remote, main_repo, agent = fixture()
(agent / "base.txt").write_text("line one\nline two changed\n")
commit_all(agent, "rewrite line")
doc = judge(agent)
assert doc["status"] == "refused" and "deleted" in doc["reason"], doc

# 4. deleting a file is refused
remote, main_repo, agent = fixture()
(agent / "base.txt").unlink()
commit_all(agent, "delete file")
doc = judge(agent)
assert doc["status"] == "refused" and "non-additive" in doc["reason"], doc

# 5. concurrent target advance still merges when the result stays additive
remote, main_repo, agent = fixture()
(agent / "own.txt").write_text("agent result\n")
commit_all(agent, "agent adds own file")
(main_repo / "other.txt").write_text("someone else\n")
git(main_repo, "add", "other.txt")
git(main_repo, "commit", "-qm", "other agent")
git(main_repo, "push", "-q", "origin", "main")
doc = judge(agent)
assert doc["status"] == "allowed", doc
tree = doc["merged_tree"]
git(agent, "cat-file", "-e", tree + ":other.txt")
git(agent, "cat-file", "-e", tree + ":own.txt")

# 6. conflicting concurrent edit is refused without touching the remote
remote, main_repo, agent = fixture()
(agent / "base.txt").write_text("line one\nagent version\n")
commit_all(agent, "agent rewrites")
(main_repo / "base.txt").write_text("line one\nmain version\n")
git(main_repo, "add", "base.txt")
git(main_repo, "commit", "-qm", "main rewrites")
git(main_repo, "push", "-q", "origin", "main")
before = remote_main(agent)
doc = judge(agent, "--execute")
assert doc["status"] == "refused" and doc["executed"] is False, doc
assert remote_main(agent) == before, "refusal must not push"

# 7. optional manifest is verified and reported
remote, main_repo, agent = fixture()
(agent / "new.txt").write_text("evidence\n")
commit_all(agent, "add evidence")
manifest = "collaboration/tasks/e0/agents/a1/checkpoints/20261114T000000Z-test/manifest.json"
run(PY, "-X", "utf8", str(CHECKPOINT), "create", "--repo", str(agent),
    "--task", "e0", "--agent", "a1", "--status", "in_progress",
    "--protocol", "protocol.md", "--artifact", "new.txt", "--out", manifest)
commit_all(agent, "add manifest")
doc = judge(agent, "--manifest", manifest)
assert doc["status"] == "allowed" and doc["manifest"] == "verified", doc

# 8. --execute refuses a dirty working tree
remote, main_repo, agent = fixture()
(agent / "new.txt").write_text("brand new\n")
commit_all(agent, "add new artifact")
(agent / "uncommitted.txt").write_text("dirty\n")
doc = judge(agent, "--execute")
assert doc["status"] == "refused" and "not clean" in doc["reason"], doc

# 9. file mode changes are refused even though numstat shows no deletions
remote, main_repo, agent = fixture()
(agent / "base.txt").chmod(0o755)
commit_all(agent, "change mode")
doc = judge(agent)
assert doc["status"] == "refused" and "mode" in doc["reason"], doc

shutil.rmtree(BASE, ignore_errors=True)
print(json.dumps({"status": "pass", "checks": [
    "additive new file + dry run is inert",
    "execute merges and pushes with remote confirmation",
    "append-only modification allowed",
    "line rewrite refused",
    "file deletion refused",
    "concurrent additive advance merges",
    "conflicting edit refused without push",
    "optional manifest verification",
    "dirty worktree refuses execute",
    "file mode change refused",
], "fixture": "local synthetic git repos; not research evidence"}, ensure_ascii=False))
