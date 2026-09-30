#!/usr/bin/env python3
"""Maintain controlled standalone mirrors; --check is read-only."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = ["references/scientific-writing-contract.md", "references/writing-adapter.md", "references/writing-examples.md",
         "assets/scientific-content-packet-template.json", "scripts/writing_adapter.py", "scripts/manuscript_lint.py", "references/theory-only-mode.md"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = []
    for name in FILES:
        source = ROOT / "skills/f-research-v1" / name
        target = ROOT / "skills/f-submit-v1" / name
        if args.check:
            if not target.is_file() or source.read_bytes() != target.read_bytes():
                errors.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    source = ROOT / "skills/f-research-v1/references/theory-only-mode.md"
    target = ROOT / "skills/f-guidance-builder-v1/references/theory-only-mode.md"
    if args.check:
        if not target.is_file() or source.read_bytes() != target.read_bytes():
            errors.append("guidance theory-only profile")
    else:
        shutil.copyfile(source, target)
    print("MIRRORS DIFFER: " + ", ".join(errors) if errors else "Controlled writing mirrors synchronized")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
