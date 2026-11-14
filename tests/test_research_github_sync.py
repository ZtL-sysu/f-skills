"""Protocol tests for the lightweight research-github-sync skill.

The skill intentionally ships no runtime scripts. These tests simulate an agent
following the written protocol inside temporary Git repositories, and check that
the templates, workflow and safety rules are actually usable.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "research-github-sync"
ASSETS = SKILL / "assets"


def run(*args, cwd=None, ok=True):
    proc = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", capture_output=True)
    if ok:
        assert proc.returncode == 0, (args, proc.stdout, proc.stderr)
    return proc


def git(repo, *args, ok=True):
    return run("git", "-C", str(repo), *args, ok=ok)


def init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.name", "Fixture")
    git(path, "config", "user.email", "fixture@example.invalid")
    return path


def init_docs(project, agent_id="codex"):
    """Simulate 'first entry': copy only missing templates, never overwrite."""
    collab = project / "collaboration"
    (collab / "agents").mkdir(parents=True, exist_ok=True)
    for name in ("STATE.md", "TASKS.md"):
        dst = collab / name
        if not dst.exists():
            shutil.copy(ASSETS / name, dst)
    agent_file = collab / "agents" / (agent_id + ".md")
    if not agent_file.exists():
        agent_file.write_text(
            (ASSETS / "AGENT.md").read_text(encoding="utf-8").replace("<agent_id>", agent_id),
            encoding="utf-8",
        )
    return collab


def clone_pair(base):
    remote = base / "remote.git"
    run("git", "init", "-q", "--bare", str(remote))
    clones = []
    for name in ("a", "b"):
        path = base / name
        run("git", "clone", "-q", str(remote), str(path))
        git(path, "config", "user.name", "Fixture")
        git(path, "config", "user.email", "fixture@example.invalid")
        clones.append(path)
    return remote, clones[0], clones[1]


class SkillContract(unittest.TestCase):
    def test_00_minimal_tree_and_no_legacy(self):
        files = sorted(str(p.relative_to(SKILL)) for p in SKILL.rglob("*") if p.is_file())
        self.assertEqual(files, [
            "SKILL.md", "agents/openai.yaml", "assets/AGENT.md",
            "assets/STATE.md", "assets/TASKS.md",
        ])
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertGreaterEqual(len(lines), 90)
        self.assertLessEqual(len(lines), 160)
        for banned in ("auto_merge.py", "checkpoint_manifest.py", "FORMAT.md",
                       "无脑合并", "每 15", "manifest.json 生成", "METRICS.csv 的固定列"):
            self.assertNotIn(banned, text)
        for required in ("STATE.md", "TASKS.md", "agents/", "先发现", "串行",
                         "force push", "git add .", "已验证", "PROTOCOL.md"):
            self.assertIn(required, text)
        ui = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        for banned in ("只多不少", "自动合并", "检查点"):
            self.assertNotIn(banned, ui)

    def test_01_new_project_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            (root / "src").mkdir(parents=True)
            (root / "src" / "main.py").write_text("print(1)\n")
            collab = init_docs(root)
            made = sorted(p.name for p in collab.rglob("*") if p.is_file())
            self.assertEqual(len(made), 3, made)
            self.assertEqual((root / "src" / "main.py").read_text(), "print(1)\n")
            (collab / "STATE.md").write_text("custom state\n", encoding="utf-8")
            init_docs(root)
            self.assertEqual((collab / "STATE.md").read_text(), "custom state\n")
            self.assertEqual(len([p for p in collab.glob("STATE*")]), 1)
            self.assertEqual(len([p for p in collab.rglob("*") if p.is_file()]), 3)
            init_docs(root, "workbuddy")
            self.assertEqual(len([p for p in (collab / "agents").glob("*.md")]), 2)
            self.assertEqual((collab / "STATE.md").read_text(), "custom state\n")

    def test_02_reuse_existing_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            (root / "experiments").mkdir(parents=True)
            readme = "# Project\n" + "long detail " * 30 + "\n"
            (root / "README.md").write_text(readme)
            (root / "AGENTS.md").write_text("Agent conventions\n")
            (root / "experiments" / "results.json").write_text('{"acc":0.9}\n')
            collab = init_docs(root)
            (collab / "STATE.md").write_text(
                "# State\n\n## Goal\nSee [README](../README.md) and [AGENTS.md](../AGENTS.md).\n\n"
                "## Verified\n- accuracy in [results.json](../experiments/results.json)\n",
                encoding="utf-8",
            )
            state = (collab / "STATE.md").read_text()
            self.assertEqual((root / "README.md").read_text(), readme)
            self.assertNotIn("long detail", state)
            self.assertIn("../README.md", state)
            self.assertIn("../experiments/results.json", state)
            self.assertEqual((root / "experiments" / "results.json").read_text(), '{"acc":0.9}\n')
            self.assertFalse((collab / "METRICS.csv").exists())
            self.assertFalse((collab / "checkpoints").exists())

    def test_03_agent_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            collab = init_docs(root, "codex")
            (collab / "STATE.md").write_text("# State\n\n## Goal\n复现 baseline 并写论文\n")
            (collab / "TASKS.md").write_text(
                "| Task | Status | Owner |\n|---|---|---|\n| baseline | doing | codex |\n")
            (collab / "agents" / "codex.md").write_text(
                "# Agent: codex\n\n## 当前任务\nbaseline 实验\n\n"
                "## 已完成\n数据加载，证据：experiments/loader.json\n\n"
                "## 关键发现\n原始划分有泄漏，改用 split_v2\n\n"
                "## 未完成与阻塞\n指标未跑完\n\n"
                "## 下一步\npython train.py --split v2\n\n"
                "## 相关位置\nexperiments/loader.json, commit abc123\n",
                encoding="utf-8",
            )
            bundle = "\n".join(p.read_text(encoding="utf-8") for p in [
                collab / "STATE.md", collab / "TASKS.md", collab / "agents" / "codex.md",
            ])
            for key in ("复现 baseline", "experiments/loader.json", "指标未跑完",
                        "python train.py --split v2", "doing", "split_v2"):
                self.assertIn(key, bundle)

    def test_04_normal_edits_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_repo(Path(tmp) / "repo")
            (repo / "code.py").write_text("def f():\n    return 1  # bug\n")
            (repo / "notes.md").write_text("结论：方法 A 有效\n错误行待删除\n")
            git(repo, "add", "code.py", "notes.md")
            git(repo, "commit", "-qm", "initial")
            first = git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "code.py").write_text("def f():\n    return 2  # fixed\n")
            (repo / "notes.md").write_text("结论：方法 A 无效（已更正）\n")
            git(repo, "add", "code.py", "notes.md")
            git(repo, "commit", "-qm", "fix bug and correct conclusion")
            self.assertEqual(len(git(repo, "log", "--oneline").stdout.strip().splitlines()), 2)
            self.assertIn("return 1", git(repo, "show", first + ":code.py").stdout)
            self.assertNotIn("错误行", (repo / "notes.md").read_text())
            text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("允许修改代码", text)
            self.assertNotIn("禁止删除已有行", text)

    def test_05_parallel_isolation_and_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote, a, b = clone_pair(base)
            (a / "collaboration" / "agents").mkdir(parents=True)
            (a / "shared.md").write_text("base\n")
            (a / "collaboration" / "agents" / "codex.md").write_text("A record\n")
            git(a, "add", "shared.md", "collaboration/agents/codex.md")
            git(a, "commit", "-qm", "base")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            git(b, "fetch", "-q", "origin")
            git(b, "checkout", "-q", "-B", "main", "FETCH_HEAD")

            (a / "a.py").write_text("A\n")
            git(a, "add", "a.py")
            git(a, "commit", "-qm", "A work")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            (b / "b.py").write_text("B\n")
            (b / "collaboration" / "agents").mkdir(parents=True, exist_ok=True)
            (b / "collaboration" / "agents" / "workbuddy.md").write_text("B record\n")
            git(b, "add", "b.py", "collaboration/agents/workbuddy.md")
            git(b, "commit", "-qm", "B work")
            self.assertNotEqual(git(b, "push", "origin", "HEAD:refs/heads/main", ok=False).returncode, 0)
            git(b, "fetch", "-q", "origin")
            merged = git(b, "merge", "--no-edit", "FETCH_HEAD", ok=False)
            self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
            git(b, "push", "-q", "origin", "HEAD:refs/heads/main")
            verify = base / "verify"
            run("git", "clone", "-q", str(remote), str(verify))
            for rel in ("a.py", "b.py", "collaboration/agents/codex.md",
                        "collaboration/agents/workbuddy.md"):
                self.assertTrue((verify / rel).exists(), rel)

            git(a, "fetch", "-q", "origin")
            git(a, "merge", "--no-edit", "FETCH_HEAD")
            (a / "shared.md").write_text("A version\n")
            git(a, "add", "shared.md")
            git(a, "commit", "-qm", "A edits shared")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            (b / "shared.md").write_text("B version\n")
            git(b, "add", "shared.md")
            git(b, "commit", "-qm", "B edits shared")
            git(b, "fetch", "-q", "origin")
            conflict = git(b, "merge", "--no-edit", "FETCH_HEAD", ok=False)
            self.assertNotEqual(conflict.returncode, 0)
            self.assertIn("<<<<<<<", (b / "shared.md").read_text())
            git(b, "merge", "--abort")

            tasks = ("| Task | Status | Owner | Scope |\n|---|---|---|---|\n"
                     "| exp | doing | codex | experiments/ |\n"
                     "| data | doing | workbuddy | experiments/ |\n")
            doing_scopes = [line.split("|")[4].strip() for line in tasks.splitlines()
                            if "| doing |" in line]
            self.assertEqual(len(doing_scopes), len(set(doing_scopes)) + 1)

    def test_06_push_rejection_keeps_local_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote, a, b = clone_pair(base)
            (a / "base.txt").write_text("base\n")
            git(a, "add", "base.txt")
            git(a, "commit", "-qm", "base")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            git(b, "fetch", "-q", "origin")
            git(b, "checkout", "-q", "-B", "main", "FETCH_HEAD")
            (a / "a.txt").write_text("A\n")
            git(a, "add", "a.txt")
            git(a, "commit", "-qm", "A")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            remote_head = run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip()

            (b / "b.txt").write_text("B\n")
            git(b, "add", "b.txt")
            git(b, "commit", "-qm", "B")
            local_head = git(b, "rev-parse", "HEAD").stdout.strip()
            rejected = git(b, "push", "origin", "HEAD:refs/heads/main", ok=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(git(b, "rev-parse", "HEAD").stdout.strip(), local_head)
            self.assertEqual(run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip(), remote_head)
            record = b / "collaboration" / "agents" / "workbuddy.md"
            record.parent.mkdir(parents=True)
            record.write_text("Sync: 未同步；本地提交 " + local_head + "；恢复：fetch + merge 后 push\n",
                              encoding="utf-8")
            self.assertNotIn("已同步", record.read_text())
            git(b, "fetch", "-q", "origin")
            git(b, "merge", "--no-edit", "FETCH_HEAD")
            git(b, "push", "-q", "origin", "HEAD:refs/heads/main")
            self.assertEqual(run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip(),
                             git(b, "rev-parse", "HEAD").stdout.strip())

    def test_07_legacy_project_compatibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            collab = root / "collaboration"
            (collab / "tasks" / "t1" / "agents" / "a1" / "checkpoints" / "c1").mkdir(parents=True)
            legacy = {
                "PROJECT.md": "Goal: reproduce baseline\n",
                "PROTOCOL.md": "Protocol v1\n",
                "tasks/t1/TASK.md": "Task t1\n",
                "tasks/t1/agents/a1/HANDOFF.md": "Handoff a1\n",
                "tasks/t1/agents/a1/checkpoints/c1/CHECKPOINT.md": "Checkpoint\n",
                "tasks/t1/agents/a1/checkpoints/c1/manifest.json": "{}\n",
                "METRICS.csv": "metric,value\nacc,0.9\n",
            }
            for rel, content in legacy.items():
                (collab / rel).write_text(content)
            before = {rel: (collab / rel).read_bytes() for rel in legacy}
            (collab / "STATE.md").write_text(
                "# State\n\n## Goal\n见 [PROJECT.md](PROJECT.md) 与 [PROTOCOL.md](PROTOCOL.md)。\n\n"
                "## Next\n见 [tasks/t1/TASK.md](tasks/t1/TASK.md)。\n",
                encoding="utf-8",
            )
            for rel, data in before.items():
                self.assertEqual((collab / rel).read_bytes(), data, rel)
            state = (collab / "STATE.md").read_text()
            self.assertIn("PROJECT.md", state)
            self.assertIn("PROTOCOL.md", state)
            self.assertIn("tasks/t1/TASK.md", state)
            self.assertTrue((collab / "tasks").is_dir())

    def test_08_sensitive_files_and_workspace_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = init_repo(base / "repo")
            (repo / "src").mkdir()
            for name, content in {"src/main.py": "print(1)\n", ".env": "SECRET=1\n",
                                  "id_rsa": "PRIVATE KEY\n", "token.txt": "fake-token-for-test\n",
                                  "weights.bin": "W" * 2048}.items():
                (repo / name).write_text(content)
            init_docs(repo)
            git(repo, "add", "--", "src/main.py", "collaboration/STATE.md",
                "collaboration/TASKS.md", "collaboration/agents/codex.md")
            staged = git(repo, "diff", "--cached", "--name-only").stdout
            for secret in (".env", "id_rsa", "token.txt", "weights.bin"):
                self.assertNotIn(secret, staged)

            repo2 = init_repo(base / "repo2")
            (repo2 / "src").mkdir()
            (repo2 / "src" / "main.py").write_text("print(1)\n")
            git(repo2, "add", "src/main.py")
            git(repo2, "commit", "-qm", "initial")
            before = git(repo2, "rev-parse", "HEAD").stdout.strip()
            (repo2 / "staged.txt").write_text("other agent staged\n")
            git(repo2, "add", "staged.txt")
            (repo2 / "dirty.txt").write_text("other agent uncommitted\n")
            staged = git(repo2, "diff", "--cached", "--name-only").stdout.strip().splitlines()
            self.assertIn("staged.txt", staged)
            self.assertEqual(git(repo2, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertIn("dirty.txt", git(repo2, "status", "--porcelain").stdout)
            self.assertEqual(git(repo2, "rev-parse", "HEAD").stdout.strip(), before)
            text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
            for rule in ("不用 `git add .`", "reset --hard", "git clean", "串行", "未同步"):
                self.assertIn(rule, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
