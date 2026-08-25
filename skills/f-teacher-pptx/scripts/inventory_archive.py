#!/usr/bin/env python3
"""Create a read-only member/hash inventory for ZIP, RAR, or 7z sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def zip_members(path: Path) -> list[dict[str, object]]:
    members: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"corrupt ZIP member: {bad}")
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise ValueError(f"ZIP contains a symbolic link, which is not accepted: {info.filename}")
            if mode and not stat.S_ISREG(mode):
                raise ValueError(f"ZIP contains a non-regular member, which is not accepted: {info.filename}")
            data = archive.read(info)
            members.append({"member": normalize_member(info.filename), "size": len(data), "sha256": digest(data)})
    return members


def normalize_member(name: str) -> str:
    normalized = name.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def validate_member_names(names: list[str]) -> None:
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ValueError(f"archive contains duplicate member paths: {duplicates}")
    dangerous = []
    for name in names:
        path = Path(name)
        if (
            not name
            or "\x00" in name
            or name.startswith(("/", "\\"))
            or bool(re.match(r"^[A-Za-z]:[/\\]", name))
            or path.is_absolute()
            or ".." in path.parts
        ):
            dangerous.append(name)
    if dangerous:
        raise ValueError(f"archive contains dangerous member paths: {dangerous}")


def seven_listing(tool: str, path: Path) -> tuple[list[str], str, str]:
    completed = subprocess.run([tool, "l", "-slt", str(path)], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"{Path(tool).name} listing failed: {(completed.stderr or completed.stdout).strip()[-1000:]}")
    blocks = completed.stdout.split("----------", 1)
    if len(blocks) != 2:
        raise RuntimeError(f"{Path(tool).name} listing did not contain a member section")
    names: list[str] = []
    for raw_block in blocks[1].split("\n\n"):
        fields: dict[str, str] = {}
        for line in raw_block.splitlines():
            if " = " in line:
                key, value = line.split(" = ", 1)
                fields[key.strip()] = value.strip()
        if fields.get("Path") and fields.get("Folder") != "+":
            names.append(normalize_member(fields["Path"]))
    version = next((line.strip() for line in completed.stdout.splitlines() if line.strip()), Path(tool).name)
    return names, completed.stdout, version


def unrar_listing(tool: str, path: Path) -> tuple[list[str], str, str]:
    completed = subprocess.run([tool, "lb", str(path)], capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"unrar listing failed: {(completed.stderr or completed.stdout).strip()[-1000:]}")
    names = [normalize_member(line.strip()) for line in completed.stdout.splitlines() if line.strip() and not line.rstrip().endswith("/")]
    version_run = subprocess.run([tool], capture_output=True, text=True, check=False)
    version_text = version_run.stdout or version_run.stderr
    version = next((line.strip() for line in version_text.splitlines() if line.strip()), Path(tool).name)
    return names, completed.stdout, version


def external_members(path: Path) -> tuple[list[dict[str, object]], str, dict[str, str]]:
    seven = shutil.which("7zz") or shutil.which("7z")
    unrar = shutil.which("unrar")
    if not seven and not unrar:
        raise RuntimeError("RAR/7z inventory requires 7zz, 7z, or unrar on PATH")
    if seven:
        listed_names, raw_listing, tool_version = seven_listing(seven, path)
        tool = Path(seven).name
    else:
        listed_names, raw_listing, tool_version = unrar_listing(unrar, path)
        tool = Path(unrar).name
    validate_member_names(listed_names)
    with tempfile.TemporaryDirectory(prefix="f-teacher-pptx-inventory-") as raw:
        target = Path(raw)
        if seven:
            command = [seven, "x", "-y", f"-o{target}", str(path)]
            tool = Path(seven).name
        else:
            command = [unrar, "x", "-idq", "-o+", str(path), str(target) + "/"]
            tool = Path(unrar).name
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[-1000:]
            raise RuntimeError(f"{tool} failed with exit {completed.returncode}: {detail}")
        members = []
        for item in sorted(target.rglob("*")):
            if item.is_symlink():
                raise ValueError(f"archive extracted a symbolic link, which is not accepted: {item.relative_to(target)}")
            if item.is_file():
                members.append({
                    "member": normalize_member(item.relative_to(target).as_posix()),
                    "size": item.stat().st_size,
                    "sha256": file_digest(item),
                })
        extracted_names = [str(item["member"]) for item in members]
        if set(extracted_names) != set(listed_names):
            missing = sorted(set(listed_names) - set(extracted_names))
            extra = sorted(set(extracted_names) - set(listed_names))
            raise ValueError(f"listed/extracted member mismatch; missing={missing}, extra={extra}")
        return members, tool, {
            "toolVersion": tool_version,
            "listingSha256": digest(raw_listing.encode("utf-8")),
            "extractedMemberSetSha256": digest("\n".join(sorted(extracted_names)).encode("utf-8")),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    archive = args.archive.expanduser().resolve()
    if not archive.is_file():
        parser.error(f"archive not found: {archive}")
    try:
        if archive.suffix.lower() == ".zip":
            members, tool = zip_members(archive), "python-zipfile"
            validate_member_names([normalize_member(str(item["member"])) for item in members])
            metadata = {
                "toolVersion": f"Python {sys.version.split()[0]} zipfile",
                "listingSha256": digest("\n".join(str(item["member"]) for item in members).encode("utf-8")),
                "extractedMemberSetSha256": digest("\n".join(sorted(str(item["member"]) for item in members)).encode("utf-8")),
            }
        elif archive.suffix.lower() in {".rar", ".7z"}:
            members, tool, metadata = external_members(archive)
        else:
            parser.error("supported extensions: .zip, .rar, .7z")
    except Exception as exc:  # noqa: BLE001
        print(f"inventory failed: {exc}", file=sys.stderr)
        return 1
    report = {
        "archive": str(archive),
        "archiveSize": archive.stat().st_size,
        "archiveSha256": file_digest(archive),
        "tool": tool,
        **metadata,
        "memberCount": len(members),
        "members": members,
    }
    output = args.json_out.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
