#!/usr/bin/env python3
"""Audit a self-contained student package and DOCX path contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ASCII_COMPONENT = re.compile(r"^[A-Za-z0-9._-]+$")
PATH_TOKEN = re.compile(r"(?<![A-Za-z0-9_])((?:ros2_ws|report|screenshots|data|reference_results)/[A-Za-z0-9_./-]+)")
GENERATED_PREFIXES = ("ros2_ws/build/", "ros2_ws/install/", "ros2_ws/log/", "results/")
TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".txt", ".py", ".xml", ".cfg"}


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    return "\n".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))


def audit(root: Path, guide_name: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "README_FIRST.txt",
        "environment.yml",
        "verify_results.py",
        guide_name,
        "wsl_miniconda_ros2_jazzy_setup.docx",
        "report/experiment_record.md",
        "ros2_ws/src",
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f"missing required path: {rel}")

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(not ASCII_COMPONENT.fullmatch(component) for component in rel.parts):
            errors.append(f"non-English or unsafe path component: {rel.as_posix()}")
        if (
            path.is_file()
            and path.suffix in TEXT_SUFFIXES
            and not (set(rel.parts) & {"build", "install", "log", "results", "__pycache__"})
        ):
            try:
                source_text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            external_roots = set(re.findall(r"experiment_\d{2}_[A-Za-z0-9_]+", source_text)) - {root.name}
            if external_roots:
                errors.append(
                    f"{rel.as_posix()} references other experiment roots: "
                    + ", ".join(sorted(external_roots))
                )

    guide = root / guide_name
    if guide.exists():
        text = docx_text(guide)
        if root.name not in text:
            warnings.append(f"guide does not visibly name package root: {root.name}")
        other_roots = set(re.findall(r"experiment_\d{2}_[A-Za-z0-9_]+", text)) - {root.name}
        if other_roots:
            errors.append("guide references other experiment roots: " + ", ".join(sorted(other_roots)))
        for token in sorted(set(PATH_TOKEN.findall(text))):
            token = token.rstrip(".,;:)")
            if token.startswith(GENERATED_PREFIXES) or "<" in token or ">" in token:
                continue
            if not (root / token).exists():
                errors.append(f"guide input path does not exist: {token}")

    return {
        "package": root.name,
        "guide": guide_name,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "ok": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--guide", default="student_guide.docx")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = audit(args.package_root.resolve(), args.guide)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
