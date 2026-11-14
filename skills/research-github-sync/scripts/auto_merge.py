"""Pure-addition auto-merge for research-github-sync.

Merge an agent branch into the target branch only when the resulting tree is a
strict superset of the current remote target tree: no deleted lines, no deleted /
renamed / copied / retyped files, and no merge conflicts. Never force-pushes,
never rewrites history, never deletes remote branches.

Default is a dry run (judge only). Pass --execute to actually merge and push.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

MANIFEST_TOOL = Path(__file__).resolve().parent / "checkpoint_manifest.py"
ALLOWED_STATUS = {"A", "M"}


class Refusal(Exception):
    pass


def git(root, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise Refusal("git %s failed: %s" % (" ".join(args[:2]), detail))
    return proc


def gout(root, *args):
    return git(root, *args).stdout.strip()


def repo_root(value):
    root = Path(value).resolve()
    top = Path(gout(root, "rev-parse", "--show-toplevel")).resolve()
    if top != root:
        raise Refusal("--repo must be the repository root")
    return root


def require_clean(root):
    if gout(root, "status", "--porcelain"):
        raise Refusal("working tree is not clean; commit or stash first")


def resolve(root, ref):
    proc = git(root, "rev-parse", "--verify", ref + "^{commit}", check=False)
    if proc.returncode != 0:
        raise Refusal("cannot resolve ref: " + ref)
    return proc.stdout.strip()


def fetch_target(root, remote, target):
    proc = git(root, "fetch", "--quiet", remote, target, check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise Refusal("fetch failed; keep the local commit and retry once: " + detail)
    return gout(root, "rev-parse", "FETCH_HEAD")


def merged_tree(root, target_commit, branch_commit):
    proc = git(root, "merge-tree", "--write-tree", target_commit, branch_commit, check=False)
    if proc.returncode != 0:
        raise Refusal(
            "three-way merge conflicts with the current target; publish a new "
            "additive checkpoint instead of resolving by deletion"
        )
    lines = proc.stdout.strip().splitlines()
    if not lines or not lines[0].strip():
        raise Refusal("merge-tree produced no tree")
    return lines[0].strip()


def additive(root, before, after):
    """Compare two tree-ish objects; accept only strict additions."""
    name_lines = [x for x in gout(root, "diff", "--name-status", "--find-renames", before, after).splitlines() if x.strip()]
    num_lines = [x for x in gout(root, "diff", "--numstat", "--find-renames", before, after).splitlines() if x.strip()]
    if not name_lines:
        raise Refusal("no change to merge")

    if "mode change" in gout(root, "diff", "--summary", before, after):
        raise Refusal("file mode changes are not additive")

    status_by_path = {}
    for line in name_lines:
        parts = line.split("\t")
        status = parts[0][0].upper()
        path = parts[-1]
        status_by_path[path] = status
        if status not in ALLOWED_STATUS:
            raise Refusal("non-additive change %s: %s" % (status, path))

    added = 0
    deleted = 0
    binary = []
    for line in num_lines:
        parts = line.split("\t", 2)
        if len(parts) < 3:
            raise Refusal("unexpected numstat output: " + line)
        a, d, path = parts
        if d == "-":
            binary.append(path)
            continue
        added += int(a)
        deleted += int(d)
    if deleted:
        raise Refusal("%d existing line(s) deleted or modified" % deleted)
    for path in binary:
        if status_by_path.get(path) != "A":
            raise Refusal("binary content change cannot be proven additive: " + path)

    files_added = sum(1 for s in status_by_path.values() if s == "A")
    files_appended = sum(1 for s in status_by_path.values() if s == "M")
    return {
        "files_added": files_added,
        "files_appended": files_appended,
        "lines_added": added,
        "lines_deleted": 0,
    }


def check_manifest(root, manifest):
    if not manifest:
        return "not_provided"
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(MANIFEST_TOOL), "verify",
         "--repo", str(root), "--manifest", manifest],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if proc.returncode != 0:
        raise Refusal("manifest verification failed: " + (proc.stderr or proc.stdout).strip())
    return "verified"


def perform(root, remote, target, target_commit, branch_commit, message):
    require_clean(root)
    head_ref = git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    previous = head_ref.stdout.strip() if head_ref.returncode == 0 else None
    git(root, "checkout", "--quiet", "--detach", target_commit)
    try:
        proc = git(root, "merge", "--no-ff", "-m", message, branch_commit, check=False)
        if proc.returncode != 0:
            git(root, "merge", "--abort", check=False)
            raise Refusal("merge failed after a clean dry run; re-run the check")
        new_head = gout(root, "rev-parse", "HEAD")
        if new_head == target_commit:
            raise Refusal("merge produced no new commit; nothing was published")
        proc = git(root, "push", remote, "HEAD:refs/heads/" + target, check=False)
        if proc.returncode != 0:
            raise Refusal(
                "push rejected; merge commit %s is kept locally (no force push)" % new_head
            )
        remote_ref = git(root, "ls-remote", remote, "refs/heads/" + target, check=False)
        if new_head not in remote_ref.stdout:
            raise Refusal("remote head not confirmed after push: " + new_head)
        return new_head
    finally:
        if previous:
            git(root, "checkout", "--quiet", previous, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--branch", required=True, help="agent branch/ref to merge")
    parser.add_argument("--target", default="main")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--manifest", help="optional checkpoint manifest to verify first")
    parser.add_argument("--message", default=None)
    parser.add_argument("--execute", action="store_true", help="merge and push; default is dry run")
    args = parser.parse_args()

    report = {
        "status": "refused",
        "target": args.target,
        "remote": args.remote,
        "branch": args.branch,
        "executed": False,
    }
    try:
        root = repo_root(args.repo)
        branch_commit = resolve(root, args.branch)
        target_commit = fetch_target(root, args.remote, args.target)
        tree = merged_tree(root, target_commit, branch_commit)
        stats = additive(root, target_commit, tree)
        verified = check_manifest(root, args.manifest)
        report.update(stats)
        report.update({
            "target_head": target_commit,
            "branch_head": branch_commit,
            "merged_tree": tree,
            "manifest": verified,
            "judgement": "additive only",
        })
        if args.execute:
            message = args.message or "auto-merge(%s): additive checkpoint only" % args.branch
            report["merge_commit"] = perform(
                root, args.remote, args.target, target_commit, branch_commit, message
            )
            report["status"] = "merged"
            report["executed"] = True
        else:
            report["status"] = "allowed"
            report["note"] = "dry run; pass --execute to merge and push"
    except (Refusal, OSError, ValueError) as exc:
        report.update({"status": "refused", "reason": str(exc)})
        print(json.dumps(report, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
