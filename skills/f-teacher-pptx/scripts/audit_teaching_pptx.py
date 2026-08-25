#!/usr/bin/env python3
"""Audit exported teaching PPTX packages for f-teacher-pptx invariants.

This is a structural gate. It does not replace slides_test.py or full-size
rendered-page review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import posixpath
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

ACTIVITY_PATTERNS = [
    r"同桌(?:交流|讨论|互动)",
    r"小组(?:讨论|合作|活动|任务|展示|汇报|互评)",
    r"分组(?:讨论|合作|任务|展示|汇报)",
    r"成果展示",
    r"作品展示",
    r"展示(?:你的|本组|小组|学习)成果",
    r"上台(?:展示|汇报|分享)",
    r"汇报交流",
    r"分享交流",
    r"同伴互评",
    r"课堂展示",
    r"角色扮演",
    r"投票评选",
]


def natural_key(path: str | Path) -> tuple[Any, ...]:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", str(path)))


def collect_pptx(inputs: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            files.extend(sorted(path.glob("*.pptx"), key=natural_key))
        elif path.is_file() and path.suffix.lower() == ".pptx":
            files.append(path)
        else:
            raise FileNotFoundError(path)
    return sorted(set(files), key=natural_key)


def xml_root(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def all_text(root: ET.Element) -> str:
    return "\n".join(node.text or "" for node in root.findall(".//a:t", NS)).strip()


def relationship_map(zf: zipfile.ZipFile, rels_path: str, owner_path: str) -> dict[str, tuple[str, str]]:
    if rels_path not in zf.namelist():
        return {}
    root = xml_root(zf, rels_path)
    mapping: dict[str, tuple[str, str]] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = rel.attrib.get("Id", "")
        target = rel.attrib.get("Target", "")
        rel_type = rel.attrib.get("Type", "")
        if target and not re.match(r"^[a-z]+://", target, flags=re.I):
            if target.startswith("/"):
                target = target.lstrip("/")
            else:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(owner_path), target))
        mapping[rel_id] = (target, rel_type)
    return mapping


def shape_name(shape: ET.Element) -> str:
    node = shape.find(".//p:cNvPr", NS)
    return node.attrib.get("name", "") if node is not None else ""


def transform_box(element: ET.Element) -> tuple[int, int, int, int] | None:
    xfrm = element.find(".//a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    try:
        return (
            int(off.attrib.get("x", "0")),
            int(off.attrib.get("y", "0")),
            int(ext.attrib.get("cx", "0")),
            int(ext.attrib.get("cy", "0")),
        )
    except ValueError:
        return None


def explicit_font_sizes(shape: ET.Element) -> list[float]:
    sizes: list[float] = []
    for tag in ("a:rPr", "a:defRPr", "a:endParaRPr"):
        for node in shape.findall(f".//{tag}", NS):
            raw = node.attrib.get("sz")
            if raw and raw.isdigit():
                sizes.append(int(raw) / 100.0)
    return sizes


def text_width_units(text: str) -> float:
    """Approximate line-width demand in em units for mixed CJK/Latin text."""
    units = 0.0
    for char in text:
        if char in "\r\n":
            continue
        if char.isspace():
            units += 0.33
        elif ord(char) >= 0x2E80:
            units += 1.0
        elif char.isalnum():
            units += 0.56
        else:
            units += 0.5
    return units


def estimated_text_capacity(shape: ET.Element, box: tuple[int, int, int, int]) -> tuple[float, float] | None:
    """Return estimated required and available height in points.

    This is deliberately conservative and only a pre-render gate. PowerPoint's
    final line breaking remains authoritative through slides_test.py and PNG QA.
    """
    _, _, width_emu, height_emu = box
    sizes = explicit_font_sizes(shape)
    if not sizes or width_emu <= 0 or height_emu <= 0:
        return None
    font_pt = max(sizes)
    body_pr = shape.find(".//a:bodyPr", NS)
    left = int(body_pr.attrib.get("lIns", "91440")) if body_pr is not None else 91440
    right = int(body_pr.attrib.get("rIns", "91440")) if body_pr is not None else 91440
    top = int(body_pr.attrib.get("tIns", "45720")) if body_pr is not None else 45720
    bottom = int(body_pr.attrib.get("bIns", "45720")) if body_pr is not None else 45720
    usable_width_pt = max((width_emu - left - right) / 12700.0, font_pt)
    lines = 0
    paragraphs = shape.findall(".//a:p", NS)
    for paragraph in paragraphs:
        paragraph_text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS))
        lines += max(1, math.ceil(text_width_units(paragraph_text) * font_pt / usable_width_pt))
    if not paragraphs:
        return None
    padding_pt = (top + bottom) / 12700.0
    required_pt = lines * font_pt * 1.25 + padding_pt
    available_pt = height_emu / 12700.0
    return required_pt * 1.15, available_pt


def role_floor(name: str, text: str, slide_number: int) -> float:
    role = name.lower()
    if "页脚" in name or "页码" in name or "footer" in role:
        return 12.0
    if any(token in name for token in ("图注", "来源", "注释")) or "caption" in role or "source" in role:
        return 16.0
    if "封面标题" in name or (slide_number == 1 and "title" in role):
        return 60.0
    if any(token in name for token in ("课次", "封面课程", "封面代码")):
        return 18.0
    if name == "标题" or "slide title" in role:
        return 40.0
    if any(token in name for token in ("卡片标题", "分区标题", "小标题")) or "card heading" in role:
        return 28.0
    if any(token in name for token in ("标注", "标签", "序号", "角标")):
        return 18.0
    if any(token in name for token in ("代码", "公式", "表格")) or any(
        token in role for token in ("code", "formula", "table")
    ):
        return 20.0
    if any(token in name for token in ("流程文字", "层级文", "比较项", "概念支点", "图中文字")):
        return 20.0
    if len(text.strip()) <= 2:
        return 18.0
    return 26.0


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value)


def note_has_field(note_text: str, field: str) -> bool:
    return bool(re.search(rf"(?im)^\s*{re.escape(field)}\s*[:：]\s*\S+", note_text))


def note_field_values(note_text: str, field: str) -> list[str]:
    return [
        value.strip()
        for value in re.findall(rf"(?im)^\s*{re.escape(field)}\s*[:：]\s*([^\r\n]+)", note_text)
        if value.strip()
    ]


def provenance_candidates(record: Any) -> list[str]:
    if isinstance(record, str):
        return [record.strip()] if record.strip() else []
    if not isinstance(record, dict):
        return []
    values: list[str] = []
    for key in ("path", "source", "directAssetUrl", "url", "promptId"):
        value = str(record.get(key, "")).strip()
        if not value:
            continue
        values.append(value)
        if key == "path":
            values.append(Path(value).name)
    return list(dict.fromkeys(item for item in values if item))


def load_plan(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("slides"), list):
        raise ValueError("plan must be an object with a slides array")
    return data


class DeckResult:
    def __init__(self, path: Path) -> None:
        self.path = str(path)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.metrics: dict[str, Any] = {}

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "status": "pass" if not self.errors else "fail",
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def audit_deck(
    path: Path,
    min_image_ratio: float,
    min_multi_ratio: float,
    min_picture_area: float,
    strict_repeated_images: bool,
    strict_text_capacity: bool,
    strict_explicit_fonts: bool,
    plan: dict[str, Any] | None,
) -> DeckResult:
    result = DeckResult(path)
    if path.stat().st_size == 0:
        result.error("file is empty")
        return result
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        result.error(f"not a valid PPTX ZIP package: {exc}")
        return result
    with zf:
        corrupt_member = zf.testzip()
        if corrupt_member:
            result.error(f"corrupt ZIP member: {corrupt_member}")
        names = set(zf.namelist())
        slide_paths = sorted(
            (
                name
                for name in names
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ),
            key=natural_key,
        )
        if not slide_paths:
            result.error("no slide XML parts found")
            return result
        planned_slides = plan.get("slides", []) if plan else []
        if plan and len(planned_slides) != len(slide_paths):
            result.error(f"plan has {len(planned_slides)} slides but PPTX has {len(slide_paths)}")

        slide_width, slide_height = 12192000, 6858000
        if "ppt/presentation.xml" in names:
            presentation = xml_root(zf, "ppt/presentation.xml")
            size = presentation.find("p:sldSz", NS)
            if size is not None:
                try:
                    slide_width = int(size.attrib.get("cx", slide_width))
                    slide_height = int(size.attrib.get("cy", slide_height))
                except ValueError:
                    result.warn("presentation slide size is not numeric; using 16:9 default")
        slide_area = max(slide_width * slide_height, 1)

        image_pages = 0
        multi_image_pages = 0
        note_pages = 0
        notes_with_sources = 0
        notes_with_visual_kind = 0
        notes_with_visual_purpose = 0
        notes_with_knowledge_source = 0
        note_assets_verified = 0
        font_violations = 0
        missing_explicit_font_shapes = 0
        outside_objects = 0
        text_capacity_violations = 0
        shrink_autofit_violations = 0
        activity_hits = 0
        image_hash_pages: dict[str, set[int]] = defaultdict(set)
        picture_counts: list[int] = []
        smallest_instructional_font: float | None = None
        planned_assets_verified = 0

        for slide_number, slide_path in enumerate(slide_paths, start=1):
            try:
                root = xml_root(zf, slide_path)
            except ET.ParseError as exc:
                result.error(f"slide {slide_number}: invalid XML: {exc}")
                continue
            text = all_text(root)
            planned = planned_slides[slide_number - 1] if slide_number <= len(planned_slides) else None
            if isinstance(planned, dict):
                planned_title = str(planned.get("title", ""))
                if planned_title and normalize_text(planned_title) not in normalize_text(text):
                    result.error(f"slide {slide_number}: planned title not found in exported slide: {planned_title!r}")
            for pattern in ACTIVITY_PATTERNS:
                if re.search(pattern, text):
                    result.error(f"slide {slide_number}: forbidden classroom-activity phrase matches /{pattern}/")
                    activity_hits += 1

            rels_path = posixpath.join(
                posixpath.dirname(slide_path),
                "_rels",
                posixpath.basename(slide_path) + ".rels",
            )
            rels = relationship_map(zf, rels_path, slide_path)

            meaningful_picture_areas: list[float] = []
            slide_media_hashes: set[str] = set()
            for picture in root.findall(".//p:pic", NS):
                box = transform_box(picture)
                if box:
                    x, y, width, height = box
                    area_ratio = max(width, 0) * max(height, 0) / slide_area
                    meaningful_picture_areas.append(area_ratio)
                    if x < 0 or y < 0 or x + width > slide_width or y + height > slide_height:
                        result.error(f"slide {slide_number}: picture extends outside canvas")
                        outside_objects += 1
                blip = picture.find(".//a:blip", NS)
                rel_id = blip.attrib.get(f"{{{NS['r']}}}embed", "") if blip is not None else ""
                target = rels.get(rel_id, ("", ""))[0]
                if target and target in names:
                    digest = hashlib.sha256(zf.read(target)).hexdigest()
                    image_hash_pages[digest].add(slide_number)
                    slide_media_hashes.add(digest)
                elif rel_id:
                    result.warn(f"slide {slide_number}: picture relationship {rel_id} has no internal media target")
            if isinstance(planned, dict):
                visual = planned.get("visual")
                assets = visual.get("assets", []) if isinstance(visual, dict) else []
                for asset in assets if isinstance(assets, list) else []:
                    if not isinstance(asset, dict):
                        continue
                    expected = str(asset.get("sha256", "")).removeprefix("sha256:").lower()
                    if not re.fullmatch(r"[0-9a-f]{64}", expected):
                        result.error(f"slide {slide_number}: planned asset lacks a valid frozen SHA-256")
                    elif expected not in slide_media_hashes:
                        result.error(
                            f"slide {slide_number}: planned asset {expected[:12]} is not embedded on its target slide"
                        )
                    else:
                        planned_assets_verified += 1
            picture_counts.append(len(meaningful_picture_areas))
            is_cover = (
                isinstance(planned, dict) and planned.get("type") == "cover"
            ) or (not plan and slide_number == 1)
            if not is_cover:
                if any(area >= min_picture_area for area in meaningful_picture_areas):
                    image_pages += 1
                elif len([area for area in meaningful_picture_areas if area >= 0.03]) >= 3:
                    image_pages += 1
                if len([area for area in meaningful_picture_areas if area >= 0.04]) >= 2:
                    multi_image_pages += 1

            for shape in root.findall(".//p:sp", NS):
                name = shape_name(shape)
                shape_text = all_text(shape)
                if not shape_text:
                    continue
                box = transform_box(shape)
                if shape.find(".//a:normAutofit", NS) is not None:
                    result.error(
                        f"slide {slide_number}: text shape {name!r} uses shrink-to-fit; grow/reflow/split the container instead"
                    )
                    shrink_autofit_violations += 1
                if box:
                    x, y, width, height = box
                    if x < 0 or y < 0 or x + width > slide_width or y + height > slide_height:
                        result.error(f"slide {slide_number}: text shape {name!r} extends outside canvas")
                        outside_objects += 1
                    capacity = estimated_text_capacity(shape, box)
                    if capacity is not None:
                        required_pt, available_pt = capacity
                        if required_pt > available_pt + 0.5:
                            message = (
                                f"slide {slide_number}: text shape {name!r} estimated to need "
                                f"{required_pt:.1f} pt height including 15% reserve, but box provides "
                                f"{available_pt:.1f} pt"
                            )
                            if strict_text_capacity:
                                result.error(message)
                            else:
                                result.warn(message + "; confirm in rendered page")
                            text_capacity_violations += 1
                sizes = explicit_font_sizes(shape)
                floor = role_floor(name, shape_text, slide_number)
                if (
                    isinstance(planned, dict)
                    and str(planned.get("title", "")).strip()
                    and normalize_text(str(planned.get("title", ""))) == normalize_text(shape_text)
                ):
                    floor = 60.0 if planned.get("type") == "cover" else 40.0
                if sizes:
                    minimum = min(sizes)
                    if floor >= 18:
                        smallest_instructional_font = (
                            minimum
                            if smallest_instructional_font is None
                            else min(smallest_instructional_font, minimum)
                        )
                    if minimum + 1e-9 < floor:
                        result.error(
                            f"slide {slide_number}: text shape {name!r} uses {minimum:g} pt below role floor {floor:g} pt"
                        )
                        font_violations += 1
                else:
                    message = f"slide {slide_number}: text shape {name!r} has no explicit font size; inherited size not verified"
                    if strict_explicit_fonts:
                        result.error(message)
                    else:
                        result.warn(message)
                    missing_explicit_font_shapes += 1

            note_target = ""
            for target, rel_type in rels.values():
                if rel_type.endswith("/notesSlide"):
                    note_target = target
                    break
            if note_target and note_target in names:
                note_pages += 1
                note_text = all_text(xml_root(zf, note_target))
                if "[Sources]" in note_text:
                    notes_with_sources += 1
                else:
                    result.error(f"slide {slide_number}: speaker notes missing [Sources]")
                if note_has_field(note_text, "knowledge.source"):
                    notes_with_knowledge_source += 1
                else:
                    result.error(f"slide {slide_number}: speaker notes missing non-empty knowledge.source")
                if note_has_field(note_text, "visual.kind"):
                    notes_with_visual_kind += 1
                else:
                    result.error(f"slide {slide_number}: speaker notes missing non-empty visual.kind")
                if note_has_field(note_text, "visual.purpose"):
                    notes_with_visual_purpose += 1
                else:
                    result.error(f"slide {slide_number}: speaker notes missing non-empty visual.purpose")
                if isinstance(planned, dict):
                    knowledge_sources = planned.get("sources", [])
                    if isinstance(knowledge_sources, list):
                        for source in knowledge_sources:
                            candidates = provenance_candidates(source)
                            if candidates and not any(candidate in note_text for candidate in candidates):
                                result.error(
                                    f"slide {slide_number}: speaker notes do not identify planned knowledge source {candidates[0]!r}"
                                )
                    visual = planned.get("visual")
                    assets = visual.get("assets", []) if isinstance(visual, dict) else []
                    if isinstance(assets, list):
                        asset_fields = note_field_values(note_text, "visual.asset")
                        if len(asset_fields) != len(assets):
                            result.error(
                                f"slide {slide_number}: speaker notes require exactly one non-empty "
                                f"visual.asset field per planned asset ({len(assets)} expected, {len(asset_fields)} found)"
                            )
                        for asset in assets:
                            candidates = provenance_candidates(asset)
                            if not candidates or not any(
                                candidate in field_value
                                for field_value in asset_fields
                                for candidate in candidates
                            ):
                                result.error(
                                    f"slide {slide_number}: no visual.asset field identifies one planned visual asset"
                                )
                            else:
                                note_assets_verified += 1
            else:
                result.error(f"slide {slide_number}: missing speaker notes part")

        planned_cover_count = sum(
            isinstance(item, dict) and item.get("type") == "cover" for item in planned_slides
        ) if plan else 1
        non_cover = max(len(slide_paths) - planned_cover_count, 1)
        image_ratio = image_pages / non_cover
        multi_ratio = multi_image_pages / non_cover
        if image_ratio + 1e-9 < min_image_ratio:
            result.error(f"meaningful-picture slide ratio {image_ratio:.3f} is below required {min_image_ratio:.3f}")
        if multi_ratio + 1e-9 < min_multi_ratio:
            result.error(f"multi-picture slide ratio {multi_ratio:.3f} is below required {min_multi_ratio:.3f}")

        repeated = {
            digest: sorted(pages)
            for digest, pages in image_hash_pages.items()
            if len(pages) > 1
        }
        for digest, pages in repeated.items():
            message = f"same embedded image {digest[:12]} appears on slides {pages}"
            if strict_repeated_images:
                result.error(message)
            else:
                result.warn(message + "; verify that it is a permitted background or pedagogically necessary reuse")

        result.metrics = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "slides": len(slide_paths),
            "notes": note_pages,
            "notesWithSources": notes_with_sources,
            "notesWithKnowledgeSource": notes_with_knowledge_source,
            "notesWithVisualKind": notes_with_visual_kind,
            "notesWithVisualPurpose": notes_with_visual_purpose,
            "noteAssetsVerified": note_assets_verified,
            "meaningfulPictureSlides": image_pages,
            "meaningfulPictureSlideRatio": round(image_ratio, 4),
            "multiPictureSlides": multi_image_pages,
            "multiPictureSlideRatio": round(multi_ratio, 4),
            "picturesPerSlide": picture_counts,
            "uniqueEmbeddedImages": len(image_hash_pages),
            "repeatedImageGroups": len(repeated),
            "smallestExplicitInstructionalFontPt": smallest_instructional_font,
            "fontViolations": font_violations,
            "shapesWithoutExplicitFontSize": missing_explicit_font_shapes,
            "outsideObjects": outside_objects,
            "estimatedTextCapacityViolations": text_capacity_violations,
            "shrinkAutofitViolations": shrink_autofit_violations,
            "forbiddenActivityHits": activity_hits,
            "plannedAssetsVerified": planned_assets_verified,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="PPTX file(s) or directories")
    parser.add_argument("--min-image-ratio", type=float, default=0.8)
    parser.add_argument("--min-multi-image-ratio", type=float, default=0.3)
    parser.add_argument("--min-picture-area", type=float, default=0.08)
    parser.add_argument("--strict-repeated-images", action="store_true")
    parser.add_argument(
        "--strict-text-capacity",
        action="store_true",
        help="fail when conservative OOXML text-height estimation lacks 15%% breathing room",
    )
    parser.add_argument(
        "--strict-explicit-fonts",
        action="store_true",
        help="fail when any visible text shape lacks an explicit final font size",
    )
    parser.add_argument("--plan", type=Path, help="frozen lesson-plan JSON; requires exactly one PPTX input")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    for name, value in (
        ("min-image-ratio", args.min_image_ratio),
        ("min-multi-image-ratio", args.min_multi_image_ratio),
        ("min-picture-area", args.min_picture_area),
    ):
        if not 0 <= value <= 1:
            parser.error(f"--{name} must be in [0, 1]")
    try:
        files = collect_pptx(args.inputs)
    except FileNotFoundError as exc:
        parser.error(f"input not found or not a PPTX: {exc}")
    if not files:
        parser.error("no PPTX files found")
    if args.plan and len(files) != 1:
        parser.error("--plan requires exactly one PPTX input")
    try:
        plan = load_plan(args.plan.expanduser().resolve() if args.plan else None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"cannot load --plan: {exc}")
    results = [
        audit_deck(
            path,
            args.min_image_ratio,
            args.min_multi_image_ratio,
            args.min_picture_area,
            args.strict_repeated_images,
            args.strict_text_capacity,
            args.strict_explicit_fonts,
            plan,
        )
        for path in files
    ]
    report = {
        "status": "pass" if all(not result.errors for result in results) else "fail",
        "decks": len(results),
        "errors": sum(len(result.errors) for result in results),
        "warnings": sum(len(result.warnings) for result in results),
        "results": [result.as_dict() for result in results],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        output = args.json_out.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
