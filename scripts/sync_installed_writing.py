#!/usr/bin/env python3
"""Guarded local skill sync: preview by default; preserve divergent installed edits."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"f-research-v1", "f-submit-v1", "f-guidance-builder-v1"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-root", type=Path, required=True)
    parser.add_argument("--backup-root", type=Path, help="new directory outside installed skills")
    parser.add_argument("--baseline-root", type=Path, help="explicit pre-edit installed snapshot; default baseline is Git HEAD")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    paths = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "skills"], cwd=ROOT, text=True).splitlines()
    changes, conflicts = [], []
    for raw in sorted(set(paths)):
        path = Path(raw)
        if len(path.parts) < 3 or path.parts[1] not in SKILLS:
            continue
        source = ROOT / path
        if not source.is_file():
            raise ValueError("deletion requires separate review: " + raw)
        relative = Path(*path.parts[1:])
        target = args.installed_root / relative
        new = source.read_bytes()
        old = target.read_bytes() if target.is_file() else None
        if old == new:
            continue
        if args.baseline_root:
            baseline = args.baseline_root / relative
            expected = baseline.read_bytes() if baseline.is_file() else None
        else:
            baseline = subprocess.run(["git", "show", "HEAD:" + raw], cwd=ROOT, capture_output=True)
            expected = baseline.stdout if baseline.returncode == 0 else None
        if old is not None and old != expected:
            conflicts.append(str(relative))
        changes.append((relative, source, target, old, new))
    if conflicts:
        print("BLOCKED: installed edits differ from repository HEAD: " + ", ".join(conflicts))
        return 1
    print(json.dumps({"mode": "apply" if args.apply else "preview", "files": [str(c[0]) for c in changes]}, indent=2))
    if not args.apply:
        return 0
    if not args.backup_root or args.backup_root.exists() or args.backup_root.resolve().is_relative_to(args.installed_root.resolve()):
        raise ValueError("--backup-root must be a new directory outside installed skills")
    args.backup_root.mkdir(parents=True)
    manifest = []
    # Snapshot all previous contents before changing any installed file.
    for relative, source, target, old, new in changes:
        if old is not None:
            backup = args.backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(old)
        manifest.append({"path": str(relative), "before_sha256": digest(old) if old is not None else None, "after_sha256": digest(new)})
    for relative, source, target, old, new in changes:
        # Recheck immediately before write in case another session changed the target.
        now = target.read_bytes() if target.is_file() else None
        if now != old:
            raise ValueError("concurrent installed change; snapshots retained: " + str(relative))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (args.backup_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("SYNCED: " + str(len(changes)) + " files; previous bytes retained in backup root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
