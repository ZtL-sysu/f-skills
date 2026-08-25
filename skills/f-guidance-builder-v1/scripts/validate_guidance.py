#!/usr/bin/env python3
"""Validate the structure of an f-research-v1 guidance Markdown file."""

from __future__ import annotations

import argparse
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
    "figures": [r"framework|architecture", r"main result table|main baseline comparison"],
    "references": [r"36", r"last 3-5 years|last three to five years|3-5"],
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


def validate(text: str, strict: bool = False) -> list[str]:
    errors: list[str] = []

    for heading in REQUIRED_SECTIONS:
        if not has_heading(text, heading):
            errors.append(f"missing required section: {heading}")
        elif strict and len(section_body(text, heading)) < 80:
            errors.append(f"section too thin for strict mode: {heading}")

    if not any(has_heading(text, heading) for heading in FIGURE_SECTION_ALIASES):
        errors.append("missing required section: Figure and Table Plan or Figure/Table Decision Rules")
    elif strict:
        fig_heading = next((heading for heading in FIGURE_SECTION_ALIASES if has_heading(text, heading)), "")
        if fig_heading and len(section_body(text, fig_heading)) < 80:
            errors.append(f"section too thin for strict mode: {fig_heading}")

    for label, patterns in REQUIRED_TERMS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE) is None:
                errors.append(f"missing required guidance element for {label}: /{pattern}/")

    outline = section_body(text, "Paper Outline")
    for idx, heading in enumerate(CANONICAL_OUTLINE, start=1):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guidance", type=Path, help="Path to guidance Markdown")
    parser.add_argument("--strict", action="store_true", help="Flag thin sections and placeholders")
    args = parser.parse_args()

    if not args.guidance.exists():
        print(f"ERROR: file not found: {args.guidance}", file=sys.stderr)
        return 2

    text = args.guidance.read_text(encoding="utf-8")
    errors = validate(text, strict=args.strict)
    if errors:
        print("Guidance validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Guidance structure is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
