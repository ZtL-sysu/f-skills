#!/usr/bin/env python3
"""Located writing candidates and integrity checks, not an automatic semantic verdict."""
import argparse
import json
import re
from pathlib import Path
from writing_adapter import SKILL, bounded, read_json, save_new, sha


def checker_versions():
    names = ["scripts/manuscript_lint.py", "scripts/writing_adapter.py", "references/scientific-writing-contract.md"]
    if (SKILL / "references/module-quality-rubric.md").is_file():
        names.append("references/module-quality-rubric.md")
    return {name: sha(SKILL / name) for name in names}

RULES = [
    ("W001", r"\b(?:P\d+[A-Z]?|S\d+[A-Z]?)\b|\b(?:audit|review) passed\b|experiment-completion-lock|f-research-v1|f-submit-v1", "possible production marker", "REMOVE_NONSCIENTIFIC or KEEP if research object"),
    ("W002", r"after the audit|to address the reviewer|JSON.{0,30}CSV|complete the evidence chain", "possible production narration", "REWRITE scientific content; retain material post-hoc disclosure"),
    ("W003", r"neither.{0,100}nor|only a toy|little can be concluded", "possible repeated defense", "NARROW or MERGE; retain uncertainty"),
    ("W004", r"proves? (?:the mechanism|equivalence)|statistically significant|causes?", "claim-strength check", "VERIFY against comparison/interval/design; no automatic deletion"),
    ("W005", r"I feel|mixed feelings|What makes this obviously AI generated", "nonacademic advice leakage", "REMOVE_NONSCIENTIFIC; preserve genuine subject quotations"),
    ("W006", r"\b(?:TODO|TBD)\b|\[INSERT RESULT\]", "unresolved placeholder", "RESOLVE before acceptance"),
]


def scan(path, root, visited=None):
    """Small conservative TeX/Markdown scanner; keeps original file/line locations."""
    visited = visited if visited is not None else set()
    path = path.resolve()
    if path in visited:
        return [], [], []
    if not path.is_relative_to(root.resolve()):
        raise ValueError("included manuscript outside run root")
    visited.add(path)
    findings, files, visible = [], [path], []
    code = False
    bibliography = False
    declaration = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.strip().startswith("```") or re.search(r"\\(?:begin|end)\{(?:verbatim|lstlisting|minted)\}", raw):
            code = not code
            continue
        if code:
            continue
        line = re.split(r"(?<!\\)%", raw, maxsplit=1)[0] if path.suffix == ".tex" else raw
        if "\\begin{thebibliography}" in line:
            bibliography = True
        if bibliography:
            if "\\end{thebibliography}" in line:
                bibliography = False
            continue
        if re.match(r"\s*(?:#+ |\\(?:sub)*section\*?\{)", line):
            declaration = bool(re.search(r"declaration|AI use|AI disclosure|acknowledg|funding|competing interest|data availability", line, re.I))
        for include in re.findall(r"\\(?:input|include)\{([^{}]+)\}", line):
            child = (path.parent / include).with_suffix(".tex") if not Path(include).suffix else path.parent / include
            f, p, v = scan(child, root, visited)
            findings.extend(f); files.extend(p); visible.extend(v)
        visible.append((str(path.relative_to(root)), number, line))
        for rule, pattern, kind, action in RULES:
            if re.search(pattern, line, re.I):
                findings.append({"rule_id": rule, "file": str(path.relative_to(root)), "line": number, "original": raw,
                                 "type": kind, "suggested_action": action,
                                 "status": "declaration-review-do-not-auto-remove" if declaration else "needs-human-judgment", "confidence": "candidate"})
    return findings, files, visible


def check(manuscript, root, policy=None, labels=None):
    policy = policy or {}
    findings, files, visible = scan(manuscript, root)
    errors = []
    text = "\n".join(v[2] for v in visible)
    # Explicit relational assertions are supplied by a fact reviewer, never inferred from a number bag.
    for assertion in policy.get("assertions", []):
        location = assertion.get("location_pattern", r"[\s\S]*")
        regions = [m.group(0) for m in re.finditer(location, text, re.I)]
        if not regions or not any(re.search(assertion["pattern"], region, re.I) for region in regions):
            errors.append("fact relationship missing/changed: " + assertion["id"])
        if assertion.get("forbidden") and any(re.search(assertion["forbidden"], r, re.I) for r in regions):
            errors.append("unsupported relationship: " + assertion["id"])
    for item in policy.get("protected_sections", []):
        original = bounded(root, item["baseline"])
        current = bounded(root, item["current"])
        files += [original, current]
        if sha(original) != item["baseline_sha256"]:
            errors.append("protected baseline changed: " + item["baseline"])
        try:
            def segment(p):
                value = p.read_bytes().decode("utf-8")
                if value.count(item["start"]) != 1 or value.count(item["end"]) != 1:
                    raise ValueError("ambiguous protected delimiters")
                a = value.index(item["start"]); b = value.index(item["end"], a) + len(item["end"])
                return value[a:b]
            if segment(original) != segment(current):
                errors.append("protected section changed: " + item["start"])
        except ValueError as exc:
            errors.append(str(exc))
    for item in policy.get("protected_artifacts", []):
        path = bounded(root, item["path"])
        files.append(path)
        if sha(path) != item["sha256"]:
            errors.append("protected artifact changed: " + item["path"])
    if labels:
        files.append(labels)
        for index, label in enumerate(read_json(labels), 1):
            for rule, pattern, kind, action in RULES[:2]:
                if re.search(pattern, label, re.I):
                    findings.append({"rule_id": rule, "file": str(labels.relative_to(root)), "line": index, "original": label, "type": "figure-label: " + kind, "suggested_action": action, "status": "needs-visual-and-human-review", "confidence": "candidate"})
    return {"schema_version": 1, "status": "integrity-failed" if errors else "semantic-review-required", "errors": errors, "findings": findings,
            "checker_versions": checker_versions(),
            "dependencies": [{"path": str(p.relative_to(root)), "sha256": sha(p)} for p in sorted(set(files))],
            "parser_limits": "Not a TeX engine: no macro expansion, conditional evaluation, bibliography rendering or OCR. Inspect rendered PDF and figures; provided labels are not proof of pixels.",
            "semantic_checks": ["facts/model-condition-direction/CI-vs-SD", "observed-vs-planned", "negative findings", "paragraph reverse outline", "Introduction-Conclusion scope", "Results-Discussion roles", "declaration routing", "rendered captions/labels"]}


def current(report, root):
    errors = ["stale/missing dependency: " + i["path"] for i in report["dependencies"]
            if not bounded(root, i["path"]).is_file() or sha(bounded(root, i["path"])) != i["sha256"]]
    if report.get("checker_versions") != checker_versions():
        errors.append("stale/missing checker, writing contract or rubric version")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--manuscript", type=Path)
    parser.add_argument("--policy", type=Path, help="relational assertions and author protection snapshots")
    parser.add_argument("--labels", type=Path, help="JSON list of visible figure labels")
    parser.add_argument("--bind", type=Path, action="append", default=[], help="also hash current PDF, source tables, figure files or package")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--check-current", type=Path)
    args = parser.parse_args()
    try:
        root = args.run_root.resolve()
        if args.check_current:
            errors = current(read_json(args.check_current), root)
            print(json.dumps({"errors": errors, "status": "stale" if errors else "hashes-current-only"}))
            return 1 if errors else 0
        if not args.manuscript or not args.report:
            raise ValueError("--manuscript and --report required for scan")
        if not args.report.resolve().is_relative_to(root):
            raise ValueError("report must be inside run root")
        report = check(args.manuscript, root, read_json(args.policy) if args.policy else None, args.labels)
        for path in [*args.bind, *([args.policy] if args.policy else [])]:
            path = path.resolve()
            if not path.is_relative_to(root):
                raise ValueError("bound dependency outside run root")
            report["dependencies"].append({"path": str(path.relative_to(root)), "sha256": sha(path)})
        save_new(args.report, report)
        print(report["status"] + "; candidates=" + str(len(report["findings"])))
        return 1 if report["errors"] else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("ERROR:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
