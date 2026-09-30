#!/usr/bin/env python3
"""Validate the structure of an f-research-v1 guidance Markdown file."""

from __future__ import annotations

import argparse
import hashlib
import json
from urllib.parse import urlparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Title / Topic",
    "Core Idea",
    "Paper Story",
    "Paper Outline",
    "Experiment Plan",
    "Expected Results",
    "Traceability Checklist",
    "Citation Scope",
]

FIGURE_SECTION_ALIASES = [
    "Figure and Table Plan",
    "Figure/Table Decision Rules",
]

REQUIRED_TERMS = {
    "dataset access": [r"Direct access URL|Source/access|Dataset"],
    "baselines": [r"Baseline"],
    "metrics": [r"Primary metric", r"Secondary metrics"],
    "failure signal": [r"Failure signal"],
    "hardware budget": [r"Runtime / Hardware Budget|Hardware Budget"],
    "traceability": [r"Must appear in paper\?"],
}

CANONICAL_OUTLINE = [
    "Introduction",
    "Related Work",
    "Method",
    "Experiments and Results",
    "Discussion",
    "Conclusion",
]

PROHIBITED_OUTLINE_TOP_LEVEL = [
    "Experimental Setup",
    "Results",
    "Ablations",
    "Ablations / Analysis",
    "Analysis",
    "Limitations",
    "Limitations and Threats to Validity",
    "Future Work",
    "Conclusion and Future Work",
]


def has_heading(text: str, heading: str) -> bool:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def section_body(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def validate(text: str, strict: bool = False, study_mode: str = "empirical") -> list[str]:
    errors: list[str] = []

    if study_mode not in {"empirical", "theory-only"}:
        return ["unknown study mode"]
    theory = study_mode == "theory-only"
    required = ["Evidence Plan" if x == "Experiment Plan" and theory else x for x in REQUIRED_SECTIONS]

    for heading in required:
        if not has_heading(text, heading):
            errors.append(f"missing required section: {heading}")
        elif strict and len(section_body(text, heading)) < 80:
            errors.append(f"section too thin for strict mode: {heading}")

    # New writing-handoff fields are optional for old contracts.
    # Citation coverage is reviewed semantically; neither a count nor a recency
    # phrase proves relevance. Explicit old author requirements remain in the file.
    if not any(has_heading(text, heading) for heading in FIGURE_SECTION_ALIASES):
        errors.append("missing required section: Figure and Table Plan or Figure/Table Decision Rules")
    elif strict:
        fig_heading = next((heading for heading in FIGURE_SECTION_ALIASES if has_heading(text, heading)), "")
        if fig_heading and len(section_body(text, fig_heading)) < 80:
            errors.append(f"section too thin for strict mode: {fig_heading}")

    terms = {"proof assumptions": [r"Assumptions"], "proof obligations": [r"Proof obligations"], "counterexample": [r"Counterexample"], "failure signal": [r"Failure signal"]} if theory else REQUIRED_TERMS
    for label, patterns in terms.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE) is None:
                errors.append(f"missing required guidance element for {label}: /{pattern}/")

    outline = section_body(text, "Paper Outline")
    headings = ["Introduction", "Related Work", "Formal Setup", "Theoretical Results", "Discussion", "Conclusion"] if theory else CANONICAL_OUTLINE
    for idx, heading in enumerate(headings, start=1):
        pattern = rf"^\s*{idx}\.\s*{re.escape(heading)}\s*:"
        if re.search(pattern, outline, flags=re.IGNORECASE | re.MULTILINE) is None:
            errors.append(f"paper outline must include canonical section {idx}: {heading}")

    prohibited = "|".join(re.escape(item) for item in PROHIBITED_OUTLINE_TOP_LEVEL)
    if re.search(rf"^\s*\d+\.\s*(?:{prohibited})\s*:", outline, flags=re.IGNORECASE | re.MULTILINE):
        errors.append("paper outline contains a prohibited non-canonical top-level section")

    if strict:
        placeholder_patterns = [
            r":\s*$",
            r"\|\s*\|\s*\|",
            r"\bTBD\b",
            r"\bTODO\b",
        ]
        for pattern in placeholder_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
                errors.append(f"strict mode found unresolved placeholder pattern: /{pattern}/")
                break

    return errors


def validate_packet(packet: Path) -> list[str]:
    errors = []
    required = [
        "startup-stage-plan.md", "idea-cards.md", "prior-art-opportunity-map.md",
        "idea-red-team-review.md", "claim-evidence-matrix.md",
        "strong-result-feasibility-contract.md", "startup-decision.md",
    ]
    for name in required:
        path = packet / name
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(f"missing or empty CCFA artifact: {name}")
    try:
        data = json.loads((packet / "feasibility-contract.json").read_text(encoding="utf-8"))
        if data.get("schema_version") != 1 or data.get("decision") != "proceed":
            errors.append("feasibility contract must use schema 1 and decision proceed")
        claims = data.get("claims")
        if not isinstance(claims, list) or not claims:
            return errors + ["nonempty claims list required"]
        identifiers = set()
        fields = """id claim mechanism assumptions falsifying_ablation dataset_url
            split_protocol primary_metric minimum expected_strong failure simple_baseline
            strong_baseline matched_control implementation_path prototype_check
            calibration_evidence test_isolation stop_return_condition""".split()
        for claim in claims:
            if not isinstance(claim, dict):
                errors.append("claim must be an object")
                continue
            for field in fields:
                value = claim.get(field)
                if not isinstance(value, str) or not value.strip() or value.strip().upper() in {"TODO", "TBD"}:
                    errors.append(f"claim missing substantive {field}")
            key = claim.get("id")
            if isinstance(key, str):
                if key in identifiers:
                    errors.append("duplicate claim id")
                identifiers.add(key)
            if claim.get("metric_direction") not in {"higher", "lower", "target"}:
                errors.append("invalid metric_direction")
            url = urlparse(str(claim.get("dataset_url", "")))
            if url.scheme not in {"http", "https"} or not url.netloc:
                errors.append("dataset_url must be HTTP(S)")
            for field in ["runtime_hours", "memory_gb", "seeds", "search_trials"]:
                value = claim.get(field)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 < value < float("inf")):
                    errors.append(f"positive finite budget required: {field}")
                elif field in {"seeds", "search_trials"} and not isinstance(value, int):
                    errors.append(f"integer budget required: {field}")
        evidence = data.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append("nonempty feasibility evidence list required")
        else:
            listed = {item.get("path") for item in evidence if isinstance(item, dict) and isinstance(item.get("path"), str)}
            for name in required:
                if name not in listed:
                    errors.append(f"CCFA artifact not hash-bound: {name}")
            for item in evidence:
                raw = item["path"]
                path = (packet / raw).resolve()
                if Path(raw).is_absolute() or not path.is_relative_to(packet.resolve()):
                    errors.append("feasibility evidence outside packet")
                elif not path.is_file() or not path.stat().st_size:
                    errors.append(f"missing evidence: {raw}")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                    errors.append(f"stale feasibility evidence: {raw}")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append(f"invalid feasibility packet: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guidance", type=Path, help="Path to guidance Markdown")
    parser.add_argument("--strict", action="store_true", help="Flag thin sections and placeholders")
    parser.add_argument("--packet", type=Path, help="Validate CCFA artifacts and feasibility-contract.json")
    parser.add_argument("--study-mode", choices=["empirical", "theory-only"], default="empirical")
    args = parser.parse_args()

    if not args.guidance.exists():
        print(f"ERROR: file not found: {args.guidance}", file=sys.stderr)
        return 2

    text = args.guidance.read_text(encoding="utf-8")
    errors = validate(text, strict=args.strict, study_mode=args.study_mode)
    if args.packet is not None:
        if args.study_mode == "theory-only":
            errors.append("theory-only uses actual proof-plan evidence, not an empirical feasibility packet")
        else:
            errors.extend(validate_packet(args.packet))
    if errors:
        print("Guidance validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Guidance structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
