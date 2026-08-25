#!/usr/bin/env python3
"""Validate strict f-teacher-pptx lesson-plan JSON files.

The script uses only the Python standard library so it can run in a local
Conda environment without installing project dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REQUIRED_TOP = {
    "courseName",
    "courseCode",
    "lessonNumber",
    "lessonTitle",
    "sourceInventoryHash",
    "fontPolicy",
    "visualPolicy",
    "slides",
}

IMAGE_KINDS = {
    "source-image",
    "web-image",
    "generated-image",
    "photo",
    "screenshot",
    "document-example",
    "chart-image",
    "map",
    "illustration",
    "real-chart",
}

SEMANTIC_KINDS = IMAGE_KINDS | {
    "diagram",
    "native-diagram",
    "equation",
    "table",
    "code",
    "formula",
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

FONT_FLOORS = {
    "coverTitle": 60,
    "slideTitle": 40,
    "body": 26,
    "diagramLabel": 20,
    "caption": 16,
    "footer": 12,
}


class Result:
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


def collect_paths(inputs: Iterable[str]) -> list[Path]:
    found: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            found.extend(sorted(path.glob("lesson_*.json")))
        elif path.is_file():
            found.append(path)
        else:
            raise FileNotFoundError(path)
    return sorted(set(found))


def as_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def asset_location(asset: Any, allow_remote: bool = False) -> str:
    if isinstance(asset, str):
        return asset.strip()
    if isinstance(asset, dict):
        return as_text(asset.get("path")) or (as_text(asset.get("url")) if allow_remote else "")
    return ""


def is_remote(location: str) -> bool:
    return bool(re.match(r"^https?://", location, flags=re.I))


def local_asset_exists(location: str, plan_path: Path) -> bool:
    if not location or is_remote(location):
        return True
    candidate = Path(location).expanduser()
    if not candidate.is_absolute():
        candidate = plan_path.parent / candidate
    return candidate.exists() and candidate.is_file()


def source_is_valid(source: Any) -> bool:
    if isinstance(source, str):
        return bool(source.strip())
    if isinstance(source, dict):
        return any(as_text(source.get(key)) for key in ("path", "url", "source", "kind"))
    return False


def contains_activity(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in ACTIVITY_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)
    return hits


def special_long_line(line: str) -> bool:
    return bool(
        re.search(r"https?://|[=$]|\b(?:SELECT|INSERT|UPDATE|DELETE|def|class|import)\b", line)
        or sum(ch.isdigit() for ch in line) > len(line) / 3
    )


def validate_asset(
    asset: Any,
    plan_path: Path,
    slide_number: int,
    result: Result,
    allow_legacy_assets: bool,
    pre_freeze: bool,
    body_len: int,
) -> str:
    location = asset_location(asset, allow_remote=pre_freeze)
    if not location:
        result.error(
            f"slide {slide_number}: visual asset has no frozen local path"
            + (" or draft url" if pre_freeze else " (use --pre-freeze only before the asset-freeze gate)")
        )
        return ""
    if not local_asset_exists(location, plan_path):
        result.error(f"slide {slide_number}: missing local visual asset: {location}")
    if isinstance(asset, str):
        message = f"slide {slide_number}: legacy bare-string asset lacks source, purpose, mapping, and alt text: {location}"
        if allow_legacy_assets:
            result.warn(message)
        else:
            result.error(message)
    elif isinstance(asset, dict):
        required_asset_keys = ["source", "purpose", "mapsTo", "alt"]
        if not pre_freeze:
            required_asset_keys.append("engagementReason")
        for key in required_asset_keys:
            value = asset.get(key)
            if key == "mapsTo":
                valid = isinstance(value, list) and bool(value)
            else:
                valid = bool(as_text(value))
            if not valid:
                result.error(f"slide {slide_number}: asset {location!r} missing {key}")
        maps_to = asset.get("mapsTo")
        if isinstance(maps_to, list) and maps_to:
            if (
                not all(isinstance(item, int) and not isinstance(item, bool) for item in maps_to)
                or len(set(maps_to)) != len(maps_to)
                or any(item < 1 or item > body_len for item in maps_to)
            ):
                result.error(
                    f"slide {slide_number}: asset {location!r} mapsTo must contain unique integers in 1..{body_len}"
                )
        if is_remote(location):
            result.warn(f"slide {slide_number}: draft remote asset is not frozen: {location}")
        else:
            for key in ("sha256", "width", "height", "date"):
                value = asset.get(key)
                valid = (
                    bool(re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", as_text(value)))
                    if key == "sha256"
                    else isinstance(value, (int, float)) and value > 0
                    if key in {"width", "height"}
                    else bool(as_text(value))
                )
                if not valid:
                    result.error(f"slide {slide_number}: frozen asset {location!r} missing/invalid {key}")
            candidate = Path(location).expanduser()
            if not candidate.is_absolute():
                candidate = plan_path.parent / candidate
            if candidate.is_file() and re.fullmatch(r"(?:sha256:)?[0-9a-fA-F]{64}", as_text(asset.get("sha256"))):
                expected = as_text(asset.get("sha256")).removeprefix("sha256:").lower()
                actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
                if actual != expected:
                    result.error(f"slide {slide_number}: frozen asset SHA-256 mismatch: {location}")
    else:
        result.error(f"slide {slide_number}: asset must be an object, got {type(asset).__name__}")
    return location


def validate_plan(
    path: Path,
    default_min_image_ratio: float,
    default_min_multi_ratio: float,
    default_max_diagram_run: int,
    allow_legacy_assets: bool,
    pre_freeze: bool,
) -> Result:
    result = Result(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        result.error(f"cannot parse JSON: {exc}")
        return result
    if not isinstance(data, dict):
        result.error("top-level value must be an object")
        return result

    missing_top = sorted(REQUIRED_TOP - set(data))
    if missing_top:
        result.error(f"missing top-level keys: {', '.join(missing_top)}")

    for key in ("courseName", "courseCode", "lessonTitle", "sourceInventoryHash"):
        if not as_text(data.get(key)):
            result.error(f"top-level {key} must be a non-empty string")
    if not isinstance(data.get("lessonNumber"), int) or data.get("lessonNumber", 0) < 1:
        result.error("lessonNumber must be a positive integer")

    source_hash = as_text(data.get("sourceInventoryHash"))
    if source_hash and not re.match(r"^(?:sha256:)?[0-9a-fA-F]{64}$", source_hash):
        result.error("sourceInventoryHash is not a SHA-256 value")

    font_policy = data.get("fontPolicy")
    if not isinstance(font_policy, dict):
        result.error("fontPolicy must be an object")
        font_policy = {}
    for role, floor in FONT_FLOORS.items():
        value = font_policy.get(role)
        if not isinstance(value, (int, float)):
            result.error(f"fontPolicy.{role} must be numeric")
        elif value < floor:
            result.error(f"fontPolicy.{role}={value} is below hard floor {floor}")

    visual_policy = data.get("visualPolicy")
    if not isinstance(visual_policy, dict):
        result.error("visualPolicy must be an object")
        visual_policy = {}
    min_image_ratio = visual_policy.get("minImageSlideRatio", default_min_image_ratio)
    min_multi_ratio = visual_policy.get("minMultiImageSlideRatio", default_min_multi_ratio)
    max_diagram_run = visual_policy.get("maxConsecutiveDiagramOnly", default_max_diagram_run)
    if not isinstance(min_image_ratio, (int, float)) or not 0 <= min_image_ratio <= 1:
        result.error("visualPolicy.minImageSlideRatio must be in [0, 1]")
        min_image_ratio = default_min_image_ratio
    if min_image_ratio < 0.8:
        rationale = as_text(visual_policy.get("rationale"))
        approval = as_text(visual_policy.get("userApproval"))
        if min_image_ratio < 0.6:
            result.error("minImageSlideRatio cannot be lower than 0.6")
        elif not rationale:
            result.error("minImageSlideRatio below 0.8 requires visualPolicy.rationale")
        elif not approval:
            result.error("minImageSlideRatio below 0.8 requires visualPolicy.userApproval documenting explicit user approval")
    if not isinstance(min_multi_ratio, (int, float)) or not 0 <= min_multi_ratio <= 1:
        result.error("visualPolicy.minMultiImageSlideRatio must be in [0, 1]")
        min_multi_ratio = default_min_multi_ratio
    if not isinstance(max_diagram_run, int) or max_diagram_run < 0:
        result.error("visualPolicy.maxConsecutiveDiagramOnly must be a non-negative integer")
        max_diagram_run = default_max_diagram_run

    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        result.error("slides must be a non-empty array")
        return result

    expected_numbers = list(range(1, len(slides) + 1))
    actual_numbers = [slide.get("slide") if isinstance(slide, dict) else None for slide in slides]
    if actual_numbers != expected_numbers:
        result.error(f"slide numbers must be contiguous and ordered 1..{len(slides)}")

    type_counts: Counter[str] = Counter()
    image_slides = 0
    multi_image_slides = 0
    diagram_run = 0
    longest_diagram_run = 0
    seen_assets: dict[str, int] = {}
    exception_pages = 0

    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            result.error(f"slide {index}: slide entry must be an object")
            continue
        number = slide.get("slide", index)
        slide_type = as_text(slide.get("type"))
        type_counts[slide_type] += 1
        title = as_text(slide.get("title"))
        teaching_goal = as_text(slide.get("teachingGoal"))
        body = slide.get("body")
        sources = slide.get("sources")
        visual = slide.get("visual")

        if not slide_type:
            result.error(f"slide {number}: missing type")
        if not title:
            result.error(f"slide {number}: missing title")
        elif len(title) > 34:
            if len(title) <= 54 and slide.get("titleLayout") == "two-line":
                result.warn(f"slide {number}: approved two-line title requires full-size render review")
            else:
                result.error(
                    f"slide {number}: title is too long for a large single-line title ({len(title)} chars); "
                    "use titleLayout=two-line for an intentional 38+ pt two-line title"
                )
        if not teaching_goal:
            result.error(f"slide {number}: missing teachingGoal")
        if not isinstance(body, list) or not body or not all(isinstance(item, str) and item.strip() for item in body):
            result.error(f"slide {number}: body must be a non-empty array of strings")
            body = []
        max_items = 6 if slide_type in {"operation", "case", "roadmap"} else 5
        if len(body) > max_items:
            result.error(f"slide {number}: {len(body)} body items exceed the {max_items}-item limit")
        for line in body:
            if len(line) > 48 and not special_long_line(line):
                result.error(f"slide {number}: body line is too long for 26+ pt text ({len(line)} chars): {line[:32]}…")
        if not isinstance(sources, list) or not sources or not all(source_is_valid(src) for src in sources):
            result.error(f"slide {number}: sources must be a non-empty array of source strings/objects")

        visible_text = "\n".join([title, teaching_goal, *body])
        for pattern in contains_activity(visible_text):
            result.error(f"slide {number}: forbidden classroom-activity phrase matches /{pattern}/")

        if slide_type == "qa":
            if not any(line.startswith("问题：") for line in body):
                result.error(f"slide {number}: Q&A body must contain a line starting with 问题：")
            if not any(line.startswith("答案：") for line in body):
                result.error(f"slide {number}: Q&A body must contain a line starting with 答案：")

        if not isinstance(visual, dict):
            result.error(f"slide {number}: visual must be an object")
            visual = {}
        visual_kind = as_text(visual.get("kind"))
        if visual_kind not in SEMANTIC_KINDS:
            result.error(f"slide {number}: unsupported or missing visual.kind: {visual_kind!r}")
        if not as_text(visual.get("purpose")):
            result.error(f"slide {number}: missing visual.purpose")
        assets = visual.get("assets", [])
        if not isinstance(assets, list):
            result.error(f"slide {number}: visual.assets must be an array")
            assets = []

        locations: list[str] = []
        for asset in assets:
            location = validate_asset(asset, path, number, result, allow_legacy_assets, pre_freeze, len(body))
            if isinstance(asset, dict) and not pre_freeze:
                source = as_text(asset.get("source"))
                is_web_asset = visual_kind == "web-image" or is_remote(source)
                is_generated_asset = visual_kind == "generated-image"
                if is_web_asset or is_generated_asset:
                    engagement = as_text(asset.get("engagementReason"))
                    if len(engagement) < 12 or engagement in {"更有趣", "增加趣味", "科技感", "增加氛围", "更吸引人"}:
                        result.error(
                            f"slide {number}: externally sourced/generated asset {location!r} requires a concrete engagementReason"
                        )
                if is_web_asset:
                    if not is_remote(source):
                        result.error(f"slide {number}: web asset {location!r} source must be its landing-page URL")
                    if not as_text(asset.get("creatorOrSite")):
                        result.error(f"slide {number}: web asset {location!r} missing creatorOrSite")
                    if not as_text(asset.get("usageNote")):
                        result.error(f"slide {number}: web asset {location!r} missing usageNote/license note")
                    if not as_text(asset.get("cropOrAnnotation")):
                        result.error(f"slide {number}: web asset {location!r} missing cropOrAnnotation record")
                if is_generated_asset and not as_text(asset.get("promptId")):
                    result.error(f"slide {number}: generated asset {location!r} missing promptId")
            if location:
                signature = location
                if not is_remote(location):
                    candidate = Path(location).expanduser()
                    if not candidate.is_absolute():
                        candidate = path.parent / candidate
                    if candidate.is_file():
                        signature = hashlib.sha256(candidate.read_bytes()).hexdigest()
                if signature in seen_assets and not bool(visual.get("allowReuse")):
                    result.error(
                        f"slide {number}: visual asset repeats slide {seen_assets[signature]} without allowReuse: {location}"
                    )
                else:
                    seen_assets[signature] = number
                locations.append(location)

        has_genuine_image = visual_kind in IMAGE_KINDS and bool(locations)
        is_cover = slide_type == "cover"
        exception = visual.get("exception")
        has_exception = isinstance(exception, dict) and bool(as_text(exception.get("reason")))
        declared_image_assets = visual_kind in IMAGE_KINDS and bool(assets)
        if not is_cover and not has_genuine_image and not has_exception and not declared_image_assets:
            result.error(f"slide {number}: non-cover slide has no genuine image asset and no documented exception")
        if visual_kind not in IMAGE_KINDS:
            spec = visual.get("spec")
            spec_has_mapping = isinstance(spec, dict) and isinstance(spec.get("mapsTo"), list) and bool(spec.get("mapsTo"))
            spec_has_content = isinstance(spec, dict) and any(
                bool(spec.get(key)) for key in ("elements", "steps", "equation", "table", "code", "relationships")
            )
            if not spec_has_mapping or not spec_has_content:
                result.error(
                    f"slide {number}: non-image semantic visual requires visual.spec with mapsTo and concrete content"
                )
            elif (
                not all(isinstance(item, int) and not isinstance(item, bool) for item in spec["mapsTo"])
                or len(set(spec["mapsTo"])) != len(spec["mapsTo"])
                or any(item < 1 or item > len(body) for item in spec["mapsTo"])
            ):
                result.error(f"slide {number}: visual.spec.mapsTo must contain unique integers in 1..{len(body)}")
        if has_exception:
            exception_pages += 1

        if not is_cover:
            if has_genuine_image:
                image_slides += 1
                diagram_run = 0
                if len(locations) >= 2:
                    multi_image_slides += 1
            else:
                diagram_run += 1
                longest_diagram_run = max(longest_diagram_run, diagram_run)

    exact_one = ("cover", "summary")
    for required in exact_one:
        if type_counts[required] != 1:
            result.error(f"lesson must contain exactly one {required} slide; found {type_counts[required]}")
    required_check_pages = max(1, (len(slides) - 1 + 29) // 30)
    for required in ("roadmap", "pitfall", "qa"):
        if type_counts[required] < required_check_pages:
            result.error(
                f"lesson requires at least {required_check_pages} {required} slide(s) for {len(slides)} total slides; "
                f"found {type_counts[required]}"
            )
    if type_counts["background"] < 1:
        result.error("lesson must contain at least one background slide")
    if type_counts["principle"] + type_counts["detail"] < 1:
        result.error("lesson must contain at least one principle or detail slide")
    if type_counts["operation"] + type_counts["case"] < 1:
        result.error("lesson must contain at least one operation or case slide")
    if slides and isinstance(slides[0], dict) and slides[0].get("type") != "cover":
        result.error("first slide must be cover")
    if slides and isinstance(slides[-1], dict) and slides[-1].get("type") != "summary":
        result.error("last slide must be summary")

    positions = {
        kind: min((i for i, slide in enumerate(slides) if isinstance(slide, dict) and slide.get("type") == kind), default=9999)
        for kind in ("background", "roadmap", "qa", "summary")
    }
    last_qa = max(
        (i for i, slide in enumerate(slides) if isinstance(slide, dict) and slide.get("type") == "qa"),
        default=-1,
    )
    core_positions = [
        i
        for i, slide in enumerate(slides)
        if isinstance(slide, dict) and slide.get("type") in {"principle", "detail", "operation", "case"}
    ]
    if core_positions and not (positions["background"] < min(core_positions) and positions["roadmap"] < min(core_positions)):
        result.error("background and roadmap must precede principle/detail/operation/case content")
    if core_positions and not (last_qa > max(core_positions) and positions["summary"] > last_qa):
        result.error("at least one final Q&A must follow core content, and summary must follow the final Q&A")

    non_cover = max(len(slides) - type_counts["cover"], 1)
    image_ratio = image_slides / non_cover
    multi_ratio = multi_image_slides / non_cover
    exception_ratio = exception_pages / non_cover
    if image_ratio + 1e-9 < float(min_image_ratio):
        result.error(f"genuine-image slide ratio {image_ratio:.3f} is below required {float(min_image_ratio):.3f}")
    if multi_ratio + 1e-9 < float(min_multi_ratio):
        result.error(f"multi-image slide ratio {multi_ratio:.3f} is below required {float(min_multi_ratio):.3f}")
    if longest_diagram_run > int(max_diagram_run):
        result.error(
            f"longest diagram-only run is {longest_diagram_run}, above maxConsecutiveDiagramOnly={max_diagram_run}"
        )
    if exception_ratio > 0.2 + 1e-9:
        result.error(f"documented visual exceptions cover {exception_ratio:.3f} of non-cover slides, above 0.200")

    result.metrics = {
        "slides": len(slides),
        "typeCounts": dict(sorted(type_counts.items())),
        "genuineImageSlides": image_slides,
        "genuineImageSlideRatio": round(image_ratio, 4),
        "multiImageSlides": multi_image_slides,
        "multiImageSlideRatio": round(multi_ratio, 4),
        "exceptionSlides": exception_pages,
        "longestDiagramOnlyRun": longest_diagram_run,
        "uniqueVisualAssets": len(seen_assets),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="lesson plan JSON file(s) or directories")
    parser.add_argument("--min-image-ratio", type=float, default=0.8)
    parser.add_argument("--min-multi-image-ratio", type=float, default=0.3)
    parser.add_argument("--max-diagram-run", type=int, default=2)
    parser.add_argument("--allow-legacy-assets", action="store_true")
    parser.add_argument(
        "--pre-freeze",
        action="store_true",
        help="allow draft URL-only assets; final plans must omit this flag and use hashed local paths",
    )
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        paths = collect_paths(args.inputs)
    except FileNotFoundError as exc:
        parser.error(f"input not found: {exc}")
    if not paths:
        parser.error("no lesson_*.json files found")

    results = [
        validate_plan(
            path,
            args.min_image_ratio,
            args.min_multi_image_ratio,
            args.max_diagram_run,
            args.allow_legacy_assets,
            args.pre_freeze,
        )
        for path in paths
    ]
    report = {
        "status": "pass" if all(not item.errors for item in results) else "fail",
        "plans": len(results),
        "errors": sum(len(item.errors) for item in results),
        "warnings": sum(len(item.warnings) for item in results),
        "results": [item.as_dict() for item in results],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        args.json_out.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        args.json_out.expanduser().resolve().write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
