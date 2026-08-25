#!/usr/bin/env python3
"""Validate a complete f-teacher-pptx course evidence chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


QA_CHECKS = (
    "content", "typography", "container", "visualRelevance",
    "legibility", "collisionFree", "teachingFlow",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def expected_hash(value: Any) -> str:
    return str(value or "").removeprefix("sha256:").lower()


def resolve(base: Path, raw: Any) -> Path:
    path = Path(str(raw or "")).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def load_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{label}: cannot parse {path}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label}: top level must be an object: {path}")
        return {}
    return data


def check_file_record(base: Path, record: Any, errors: list[str], label: str) -> Path | None:
    if not isinstance(record, dict) or not record.get("path"):
        errors.append(f"{label}: requires path and sha256")
        return None
    path = resolve(base, record["path"])
    if not path.is_file():
        errors.append(f"{label}: file not found: {path}")
        return None
    wanted = expected_hash(record.get("sha256"))
    if not re.fullmatch(r"[0-9a-f]{64}", wanted):
        errors.append(f"{label}: invalid sha256")
    elif sha256(path) != wanted:
        errors.append(f"{label}: sha256 mismatch: {path}")
    return path


def check_gate_record(
    base: Path,
    record: Any,
    errors: list[str],
    label: str,
    required_command_tokens: tuple[str, ...],
    require_json_pass: bool,
    forbidden_command_tokens: tuple[str, ...] = (),
    require_zero_warnings: bool = False,
) -> Path | None:
    if not isinstance(record, dict):
        errors.append(f"{label}: execution record is missing")
        return None
    command = str(record.get("command", "")).strip()
    if not command:
        errors.append(f"{label}: command is missing")
    for token in required_command_tokens:
        if token not in command:
            errors.append(f"{label}: command is missing required token {token!r}")
    for token in forbidden_command_tokens:
        if token in command:
            errors.append(f"{label}: command contains forbidden final-gate token {token!r}")
    if record.get("exitCode") != 0:
        errors.append(f"{label}: exitCode must be 0")
    report_path = check_file_record(base, record.get("report"), errors, f"{label} report")
    if report_path and require_json_pass:
        report = load_json(report_path, errors, f"{label} report")
        if report.get("status") != "pass":
            errors.append(f"{label}: JSON report status is not pass")
        if int(report.get("errors", 0) or 0) != 0:
            errors.append(f"{label}: JSON report contains errors")
        if require_zero_warnings and int(report.get("warnings", 0) or 0) != 0:
            errors.append(f"{label}: final JSON report must contain zero warnings")
    return report_path


def pptx_slide_count(path: Path, errors: list[str], label: str) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            return sum(bool(re.fullmatch(r"ppt/slides/slide\d+\.xml", name)) for name in archive.namelist())
    except (zipfile.BadZipFile, OSError) as exc:
        errors.append(f"{label}: invalid PPTX: {exc}")
        return 0


def pptx_cover_text(path: Path, errors: list[str], label: str) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
        return "".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
    except (KeyError, ET.ParseError, zipfile.BadZipFile, OSError) as exc:
        errors.append(f"{label}: cannot read cover text: {exc}")
        return ""


def png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read PNG dimensions without adding an image-library dependency."""
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def is_iso_datetime(value: Any) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", str(value or "")))


def validate(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_json(path, errors, "manifest")
    base = path.parent
    for key in ("courseName", "courseCode"):
        if not str(manifest.get(key, "")).strip():
            errors.append(f"manifest: missing {key}")
    inventory_path = None
    for key in ("syllabus", "schedule", "sourceInventory"):
        checked = check_file_record(base, manifest.get(key), errors, key)
        if key == "sourceInventory":
            inventory_path = checked
    inventory_hash = sha256(inventory_path) if inventory_path else ""

    archive_members: set[str] = set()
    archive_inventories = manifest.get("archiveInventories", [])
    if not isinstance(archive_inventories, list):
        errors.append("manifest: archiveInventories must be an array")
        archive_inventories = []
    archive_ids: set[str] = set()
    for index, record in enumerate(archive_inventories, 1):
        archive_id = str(record.get("id", "")).strip() if isinstance(record, dict) else ""
        if not archive_id or archive_id in archive_ids or "::" in archive_id:
            errors.append(f"archive inventory {index}: id must be unique, non-empty, and not contain ::")
            continue
        archive_ids.add(archive_id)
        inventory_file = check_file_record(base, record, errors, f"archive inventory {archive_id}")
        if not inventory_file:
            continue
        inventory_data = load_json(inventory_file, errors, f"archive inventory {archive_id}")
        members = inventory_data.get("members")
        if not isinstance(members, list):
            errors.append(f"archive inventory {archive_id}: members must be an array")
            continue
        for member in members:
            name = str(member.get("member", "")).strip() if isinstance(member, dict) else ""
            if not name:
                errors.append(f"archive inventory {archive_id}: member missing name")
            else:
                archive_members.add(f"{archive_id}::{name}")

    source_files = manifest.get("sourceFiles", [])
    if not isinstance(source_files, list):
        errors.append("manifest: sourceFiles must be an array")
        source_files = []
    for index, record in enumerate(source_files, 1):
        source_id = str(record.get("id", "")).strip() if isinstance(record, dict) else ""
        if not source_id or source_id in archive_ids or source_id in archive_members or "::" in source_id:
            errors.append(f"source file {index}: id must be unique, non-empty, and not contain ::")
            continue
        archive_ids.add(source_id)
        if check_file_record(base, record, errors, f"source file {source_id}"):
            archive_members.add(source_id)
    if not archive_members:
        errors.append("manifest: at least one archive member or direct sourceFiles entry is required")

    lessons = manifest.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        errors.append("manifest: lessons must be a non-empty array")
        lessons = []
    numbers = [item.get("lessonNumber") if isinstance(item, dict) else None for item in lessons]
    if numbers != list(range(1, len(lessons) + 1)):
        errors.append(f"manifest: lessonNumber values must be contiguous and ordered 1..{len(lessons)}")

    total_slides = 0
    total_pages = 0
    mapped_members: set[str] = set()
    formal_paths: set[Path] = set()
    for index, lesson in enumerate(lessons, 1):
        label = f"lesson {index}"
        if not isinstance(lesson, dict):
            errors.append(f"{label}: must be an object")
            continue
        if not str(lesson.get("lessonTitle", "")).strip():
            errors.append(f"{label}: missing lessonTitle")
        members = lesson.get("sourceMembers")
        if not isinstance(members, list) or not members or not all(str(item).strip() for item in members):
            errors.append(f"{label}: sourceMembers must identify at least one inventoried archive/deck member")
        else:
            for member in members:
                member = str(member)
                mapped_members.add(member)
                if member not in archive_members:
                    errors.append(f"{label}: source member/unit is not present in archive inventories or sourceFiles: {member}")
        plan_path = check_file_record(base, lesson.get("plan"), errors, f"{label} plan")
        plan_audit_path = check_gate_record(
            base, lesson.get("planAudit"), errors, f"{label} planAudit",
            ("validate_lesson_plan.py", "--json-out"), True,
            forbidden_command_tokens=("--pre-freeze",), require_zero_warnings=True,
        )
        build_manifest_path = check_file_record(base, lesson.get("buildManifest"), errors, f"{label} buildManifest")
        pptx_path = check_file_record(base, lesson.get("pptx"), errors, f"{label} pptx")
        check_gate_record(
            base, lesson.get("staticAudit"), errors, f"{label} staticAudit",
            (
                "audit_teaching_pptx.py", "--strict-repeated-images",
                "--strict-text-capacity", "--strict-explicit-fonts", "--json-out",
            ), True,
        )
        check_gate_record(
            base, lesson.get("slidesTest"), errors, f"{label} slidesTest",
            ("slides_test.py",), False,
        )
        formal_path = check_file_record(base, lesson.get("formalPptx"), errors, f"{label} formalPptx")
        if formal_path:
            formal_paths.add(formal_path.resolve())
        expected = lesson.get("expectedSlides")
        if not isinstance(expected, int) or expected < 1:
            errors.append(f"{label}: expectedSlides must be a positive integer")
            expected = 0
        actual = pptx_slide_count(pptx_path, errors, label) if pptx_path else 0
        if pptx_path and formal_path and sha256(pptx_path) != sha256(formal_path):
            errors.append(f"{label}: formal PPTX does not hash-match the verified staging PPTX")
        if formal_path:
            cover = pptx_cover_text(formal_path, errors, label)
            for identity in (manifest.get("courseName"), manifest.get("courseCode"), lesson.get("lessonTitle")):
                if str(identity or "").strip() and re.sub(r"\s+", "", str(identity)) not in re.sub(r"\s+", "", cover):
                    errors.append(f"{label}: formal PPTX cover does not contain identity {identity!r}")
        if expected and actual != expected:
            errors.append(f"{label}: PPTX has {actual} slides, expected {expected}")
        planned_asset_hashes_by_slide: dict[int, set[str]] = {}
        if plan_path:
            plan = load_json(plan_path, errors, f"{label} plan")
            if plan.get("courseName") != manifest.get("courseName") or plan.get("courseCode") != manifest.get("courseCode"):
                errors.append(f"{label}: plan course identity differs from manifest")
            if expected_hash(plan.get("sourceInventoryHash")) != inventory_hash:
                errors.append(f"{label}: plan sourceInventoryHash differs from the inventoried source file")
            if plan.get("lessonNumber") != index or plan.get("lessonTitle") != lesson.get("lessonTitle"):
                errors.append(f"{label}: plan lesson identity differs from manifest")
            if isinstance(plan.get("slides"), list) and len(plan["slides"]) != expected:
                errors.append(f"{label}: plan has {len(plan['slides'])} slides, expected {expected}")
            for planned_slide in plan.get("slides", []) if isinstance(plan.get("slides"), list) else []:
                if not isinstance(planned_slide, dict) or not isinstance(planned_slide.get("slide"), int):
                    continue
                visual = planned_slide.get("visual")
                assets = visual.get("assets", []) if isinstance(visual, dict) else []
                planned_asset_hashes_by_slide[planned_slide["slide"]] = {
                    expected_hash(asset.get("sha256"))
                    for asset in assets
                    if isinstance(asset, dict) and re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", str(asset.get("sha256", "")))
                }
        if plan_audit_path and plan_path:
            plan_audit = load_json(plan_audit_path, errors, f"{label} planAudit report")
            audited_paths = {
                resolve(plan_audit_path.parent, item.get("path")).resolve()
                for item in plan_audit.get("results", [])
                if isinstance(item, dict) and str(item.get("path", "")).strip()
            }
            if plan_path.resolve() not in audited_paths:
                errors.append(f"{label}: planAudit report does not identify the lesson plan path")

        if build_manifest_path:
            build = load_json(build_manifest_path, errors, f"{label} build manifest")
            build_base = build_manifest_path.parent
            builder_path = check_file_record(build_base, build.get("builder"), errors, f"{label} builder")
            if builder_path is None:
                errors.append(f"{label}: build manifest must bind the exact builder file")
            if expected_hash(build.get("sourceInventorySha256")) != inventory_hash:
                errors.append(f"{label}: build manifest sourceInventorySha256 mismatch")
            if plan_path and expected_hash(build.get("planSha256")) != sha256(plan_path):
                errors.append(f"{label}: build manifest planSha256 mismatch")
            if pptx_path and expected_hash(build.get("outputPptxSha256")) != sha256(pptx_path):
                errors.append(f"{label}: build manifest outputPptxSha256 mismatch")
            asset_hashes = build.get("assetSha256s")
            if (
                not isinstance(asset_hashes, list)
                or asset_hashes != sorted(set(asset_hashes))
                or any(not re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", str(item)) for item in asset_hashes)
            ):
                errors.append(f"{label}: build manifest assetSha256s must be a sorted unique SHA-256 array")
            runtime = build.get("runtime")
            if not isinstance(runtime, dict) or any(
                not str(runtime.get(key, "")).strip()
                for key in ("node", "nodeModules", "binDir", "nodeVersion", "artifactToolVersion")
            ):
                errors.append(f"{label}: build manifest runtime fingerprint is incomplete")
            if not str(build.get("exportCommand", "")).strip():
                errors.append(f"{label}: build manifest exportCommand is missing")

        render_manifest_path = resolve(base, lesson.get("renderManifest"))
        render_manifest = load_json(render_manifest_path, errors, f"{label} render manifest") if render_manifest_path.is_file() else {}
        if not render_manifest_path.is_file():
            errors.append(f"{label}: render manifest not found: {render_manifest_path}")
        pptx_hash = sha256(pptx_path) if pptx_path and pptx_path.is_file() else ""
        if expected_hash(render_manifest.get("pptxSha256")) != pptx_hash:
            errors.append(f"{label}: render manifest does not identify the final PPTX hash")
        pages = render_manifest.get("pages")
        if not isinstance(pages, list):
            pages = []
        page_numbers = [page.get("slide") if isinstance(page, dict) else None for page in pages]
        if page_numbers != list(range(1, expected + 1)):
            errors.append(f"{label}: render manifest must cover slides 1..{expected} exactly once")
        render_dir = resolve(base, lesson.get("renderDir"))
        rendered_by_slide: dict[int, Path] = {}
        for page in pages:
            if not isinstance(page, dict):
                continue
            image_path = resolve(render_dir, page.get("path"))
            if isinstance(page.get("slide"), int):
                rendered_by_slide[page["slide"]] = image_path
            if not image_path.is_file():
                errors.append(f"{label}: rendered page missing: {image_path}")
            elif expected_hash(page.get("sha256")) != sha256(image_path):
                errors.append(f"{label}: rendered page hash mismatch: {image_path}")

        qa_path = resolve(base, lesson.get("qaReport"))
        qa = load_json(qa_path, errors, f"{label} QA") if qa_path.is_file() else {}
        if not qa_path.is_file():
            errors.append(f"{label}: QA report not found: {qa_path}")
        if expected_hash(qa.get("pptxSha256")) != pptx_hash:
            errors.append(f"{label}: QA report does not identify the final PPTX hash")
        if qa.get("schemaVersion") != 2:
            errors.append(f"{label}: final QA must use schemaVersion 2")
        reviewer = qa.get("reviewer")
        if not isinstance(reviewer, dict) or any(not str(reviewer.get(key, "")).strip() for key in ("type", "name")):
            errors.append(f"{label}: QA reviewer requires type and name")
        if not is_iso_datetime(qa.get("reviewedAt")):
            errors.append(f"{label}: QA reviewedAt must be timezone-aware ISO 8601")
        if qa.get("viewMode") not in {"100-percent", "native-resolution"}:
            errors.append(f"{label}: QA viewMode must be 100-percent or native-resolution")
        render_record = qa.get("render")
        if not isinstance(render_record, dict):
            render_record = {}
            errors.append(f"{label}: QA render fingerprint is missing")
        for key in ("renderer", "rendererVersion", "command"):
            if not str(render_record.get(key, "")).strip():
                errors.append(f"{label}: QA render.{key} is missing")
        if not is_iso_datetime(render_record.get("renderedAt")):
            errors.append(f"{label}: QA render.renderedAt must be timezone-aware ISO 8601")
        for key in ("requestedWidth", "requestedHeight", "actualWidth", "actualHeight"):
            if not isinstance(render_record.get(key), int) or render_record[key] < 1:
                errors.append(f"{label}: QA render.{key} must be a positive integer")
        if qa.get("renderedPages") != expected or qa.get("reviewedPages") != expected:
            errors.append(f"{label}: QA renderedPages and reviewedPages must both equal {expected}")
        reviews = qa.get("pages")
        if not isinstance(reviews, list):
            reviews = []
        review_numbers = [page.get("slide") if isinstance(page, dict) else None for page in reviews]
        if review_numbers != list(range(1, expected + 1)):
            errors.append(f"{label}: QA report must review slides 1..{expected} exactly once")
        for page in reviews:
            if not isinstance(page, dict):
                continue
            slide = page.get("slide")
            evidence = resolve(base, page.get("evidence"))
            expected_evidence = rendered_by_slide.get(slide)
            if not str(page.get("evidence", "")).strip():
                errors.append(f"{label} slide {slide}: QA evidence path is missing")
            elif expected_evidence is None or evidence != expected_evidence:
                errors.append(f"{label} slide {slide}: QA evidence is not the corresponding rendered PNG")
            elif not evidence.is_file():
                errors.append(f"{label} slide {slide}: QA evidence file does not exist: {evidence}")
            else:
                if expected_hash(page.get("evidenceSha256")) != sha256(evidence):
                    errors.append(f"{label} slide {slide}: QA evidenceSha256 mismatch")
                dimensions = png_dimensions(evidence)
                if dimensions is None:
                    errors.append(f"{label} slide {slide}: QA evidence is not a readable PNG")
                elif (page.get("actualWidth"), page.get("actualHeight")) != dimensions:
                    errors.append(f"{label} slide {slide}: QA page dimensions do not match the rendered PNG")
                elif (render_record.get("actualWidth"), render_record.get("actualHeight")) != dimensions:
                    errors.append(f"{label} slide {slide}: QA page dimensions differ from the renderer fingerprint")
            for check in QA_CHECKS:
                if page.get(check) is not True:
                    errors.append(f"{label} slide {slide}: QA check {check} is not true")
            if page.get("status") != "pass":
                errors.append(f"{label} slide {slide}: QA status is not pass")
            review_note = str(page.get("reviewNote", "")).strip()
            if len(review_note) < 20 or review_note in {"全部通过", "无问题", "检查通过", "all checks passed"}:
                errors.append(f"{label} slide {slide}: QA reviewNote must contain concrete visual observations")
            assets = page.get("assets")
            if not isinstance(assets, list):
                errors.append(f"{label} slide {slide}: QA assets must be an array")
                assets = []
            reviewed_asset_hashes: set[str] = set()
            for asset_index, asset in enumerate(assets, 1):
                if not isinstance(asset, dict):
                    errors.append(f"{label} slide {slide}: QA asset {asset_index} must be an object")
                    continue
                if not re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", str(asset.get("assetSha256", ""))):
                    errors.append(f"{label} slide {slide}: QA asset {asset_index} has invalid assetSha256")
                else:
                    reviewed_asset_hashes.add(expected_hash(asset.get("assetSha256")))
                if asset.get("cropMode") not in {"contain", "cover", "crop", "full-bleed", "native"}:
                    errors.append(f"{label} slide {slide}: QA asset {asset_index} has invalid cropMode")
                area = asset.get("visibleAreaRatio")
                if not isinstance(area, (int, float)) or not 0 < area <= 1:
                    errors.append(f"{label} slide {slide}: QA asset {asset_index} has invalid visibleAreaRatio")
                if asset.get("relevanceVerdict") != "pass" or len(str(asset.get("observation", "")).strip()) < 12:
                    errors.append(f"{label} slide {slide}: QA asset {asset_index} lacks a concrete passing relevance observation")
            planned_hashes = planned_asset_hashes_by_slide.get(slide, set())
            if reviewed_asset_hashes != planned_hashes:
                errors.append(
                    f"{label} slide {slide}: QA asset hashes differ from the frozen plan; "
                    f"missing={sorted(planned_hashes - reviewed_asset_hashes)}, "
                    f"unexpected={sorted(reviewed_asset_hashes - planned_hashes)}"
                )
            issues = page.get("issues")
            if not isinstance(issues, list):
                errors.append(f"{label} slide {slide}: QA issues must be an array")
            else:
                for issue_index, issue in enumerate(issues, 1):
                    resolved = isinstance(issue, dict) and (
                        issue.get("resolved") is True or issue.get("status") in {"fixed", "resolved"}
                    )
                    if not resolved:
                        errors.append(
                            f"{label} slide {slide}: QA issue {issue_index} is not explicitly fixed/resolved"
                        )
        if qa.get("status") != "pass":
            errors.append(f"{label}: final QA status is not pass")
        total_slides += actual
        total_pages += len(pages)

    excluded = manifest.get("excludedSourceMembers", [])
    if not isinstance(excluded, list) or any(
        not isinstance(item, dict) or not str(item.get("member", "")).strip() or not str(item.get("reason", "")).strip()
        for item in excluded
    ):
        errors.append("manifest: excludedSourceMembers entries require member and reason")
        excluded = []
    excluded_members = {str(item["member"]) for item in excluded if isinstance(item, dict) and item.get("member")}
    unknown_excluded = excluded_members - archive_members
    if unknown_excluded:
        errors.append(f"manifest: excluded source units not found in inventories: {sorted(unknown_excluded)}")
    overlap = mapped_members & excluded_members
    if overlap:
        errors.append(f"manifest: members cannot be both mapped and excluded: {sorted(overlap)}")
    uncovered = archive_members - mapped_members - excluded_members
    if uncovered:
        errors.append(f"manifest: archive members are neither mapped nor excluded: {sorted(uncovered)}")
    formal_dir = resolve(base, manifest.get("formalDirectory"))
    if not str(manifest.get("formalDirectory", "")).strip() or not formal_dir.is_dir():
        errors.append(f"manifest: formalDirectory is missing or not a directory: {formal_dir}")
    else:
        actual_formal = {item.resolve() for item in formal_dir.glob("*.pptx") if item.is_file()}
        if actual_formal != formal_paths:
            errors.append(
                "manifest: formalDirectory PPTX set differs from formalPptx records; "
                f"unrecorded={sorted(map(str, actual_formal - formal_paths))}, "
                f"missing={sorted(map(str, formal_paths - actual_formal))}"
            )
    return {
        "status": "pass" if not errors else "fail",
        "path": str(path),
        "errors": errors,
        "warnings": warnings,
        "metrics": {"lessons": len(lessons), "slides": total_slides, "renderedPages": total_pages},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    path = args.manifest.expanduser().resolve()
    if not path.is_file():
        parser.error(f"manifest not found: {path}")
    report = validate(path)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        output = args.json_out.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
