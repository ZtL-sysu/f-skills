#!/usr/bin/env python3
"""Build bounded writer inputs; never invokes a model, CLI, experiment or network."""
import argparse
import hashlib
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
STAGES = {"P6", "P7", "P10", "P19", "P20", "P21", "S7", "S8", "S9"}
STATUSES = {"observed_verified", "derived_verified", "author_reported", "planned", "unresolved"}
ACTIONS = {"KEEP", "REWRITE", "MOVE", "MERGE", "NARROW", "REMOVE_NONSCIENTIFIC", "BLOCK_EVIDENCE"}
SECTION_JOBS = {
    "abstract": "Give the question, design, a few main findings and meaning. Include only qualifications that change those claims; mechanism non-identification is not an obligatory closing sentence for a predictive claim.",
    "introduction": "State the specific unresolved question and the actual comparison used to answer it. Do not add unsupported domain background as established fact.",
    "methods": "Explain scientific operations and conditions, including selection and measurement scope. Put execution history outside the text.",
    "results": "Lead with the principal comparison, effect and uncertainty, including adverse findings. Protocol belongs in Methods; retain a local condition only when needed to interpret the result.",
    "discussion": "Add interpretation of the reported pattern or trade-off and its supported use. Do not replay the score inventory or all method boundaries. Label mechanisms as hypotheses when needed.",
    "conclusion": "Answer the opening question using supported main evidence. Avoid a closing list of every untested mechanism/application.",
    "local-revision": "Replace the defective passage using relevant facts; keep unrelated findings and qualifiers in their appropriate sections. An explicit KEEP decision returns identical manuscript bytes.",
}
BRIEF_FIELDS = {"question", "answer", "audience", "domain_bridge", "priorities", "terminology", "section_jobs", "style", "journal_requirements", "author_constraints", "study_type", "paragraph_plan", "qualification_placement"}
FACT_FIELDS = {"id", "kind", "statement", "status", "model", "condition", "metric", "value", "unit", "aggregation", "uncertainty", "measurement_scope", "claim_strength", "evidence", "assumptions", "proof", "attribution", "verification_note", "citation"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def bounded(root, raw):
    path = (root / raw).resolve()
    if Path(raw).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("path outside run root: " + raw)
    return path


def save_new(path, obj):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def dependency(name, installed_root=None):
    if name not in {"humanizer", "paper-refine", "paper-polish-workflow", "ml-paper-writing"}:
        raise ValueError("unsupported subordinate writer")
    roots = [Path(installed_root)] if installed_root else [Path.home() / ".codex/skills"]
    candidates = [p / name / "SKILL.md" for p in roots]
    candidates += [SKILL / "bundled-skills" / name / "SKILL.md"]
    candidates += [p / "f-research-v1/bundled-skills" / name / "SKILL.md" for p in roots]
    for path in candidates:
        if path.is_file():
            return {"name": name, "path": str(path.resolve()), "sha256": sha(path)}
    return {"name": name, "path": None, "sha256": None, "status": "unavailable"}


def build(packet, root, stage, section, subskill=None, installed_root=None, source=None, edits=None, section_role=None):
    if stage not in STAGES:
        raise ValueError("unsupported writing stage")
    if packet.get("schema_version") != 1:
        raise ValueError("packet schema_version must be 1")
    brief = packet.get("brief", {})
    if not isinstance(brief, dict) or set(brief) - BRIEF_FIELDS:
        raise ValueError("unknown brief field; keep operations outside manuscript brief")
    for key in ("question", "audience", "section_jobs"):
        if not brief.get(key):
            raise ValueError("missing brief field: " + key)
    facts = packet.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ValueError("nonempty scientific facts required")
    clean, verify, ids = [], [], set()
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) - FACT_FIELDS:
            raise ValueError("unknown fact field; translate logs into scientific facts first")
        if not fact.get("id") or fact["id"] in ids:
            raise ValueError("fact IDs must be unique and nonempty")
        ids.add(fact["id"])
        if fact.get("status") not in STATUSES or not fact.get("statement"):
            raise ValueError("fact requires valid status and manuscript-ready statement")
        if fact.get("kind") not in {"method", "result", "theorem", "limitation", "reference", "figure", "hypothesis", "disclosure", "definition"}:
            raise ValueError("invalid scientific fact kind")
        if fact["kind"] == "theorem" and (not fact.get("assumptions") or not fact.get("proof")):
            raise ValueError("theorem requires explicit assumptions and proof text")
        if fact["kind"] == "reference" and fact["status"] in {"observed_verified", "author_reported"}:
            citation = fact.get("citation")
            if not isinstance(citation, dict) or not all(citation.get(k) for k in ("authors", "title", "year", "url")):
                raise ValueError("reported/verified reference needs citation authors/title/year/url; recover metadata before drafting")
        if fact["status"] == "derived_verified" and (brief.get("study_type") != "theoretical" or fact["kind"] not in {"theorem", "definition"}):
            raise ValueError("derived_verified belongs to theoretical propositions, not observed metrics")
        if fact["kind"] == "result":
            for key in ("model", "condition", "metric", "value", "unit", "aggregation", "uncertainty", "measurement_scope"):
                if key not in fact or fact[key] in (None, ""):
                    raise ValueError("result missing " + key + ": " + fact["id"])
        evidence = fact.get("evidence", [])
        if fact["status"] in {"observed_verified", "derived_verified", "author_reported"} and not evidence:
            raise ValueError("reported/verified fact needs evidence or author-source snapshot")
        for item in evidence:
            path = bounded(root, item["path"])
            if not path.is_file() or item.get("sha256") != sha(path):
                raise ValueError("missing/stale evidence: " + item["path"])
            verify.append({"fact_id": fact["id"], **item})
        clean.append({k: v for k, v in fact.items() if k not in {"evidence", "verification_note"}})
    if section_role == "results":
        if brief.get("study_type") == "theoretical":
            if not any(f["kind"] in {"theorem", "definition", "result"} and f["status"] in {"derived_verified", "observed_verified", "author_reported"} for f in facts):
                raise ValueError("theoretical Results needs supported propositions/proof evidence")
        elif not any(f["kind"] == "result" and f["status"] in {"observed_verified", "author_reported"} for f in facts):
            raise ValueError("empirical Results needs reported/verified result facts, not a plan")
    # A structural repair is a positive argument plan, not another list of bans.
    # Optional for legacy packets and simple local edits; validate references when used.
    plan = brief.get("paragraph_plan", [])
    if not isinstance(plan, list):
        raise ValueError("paragraph_plan must be a list")
    paragraph_ids = set()
    for move in plan:
        if not isinstance(move, dict) or set(move) != {"id", "section", "point", "fact_ids", "adds"}:
            raise ValueError("paragraph plan requires id/section/point/fact_ids/adds")
        if any(not isinstance(move[k], str) or not move[k].strip() for k in ("id", "section", "point", "adds")) or move["id"] in paragraph_ids:
            raise ValueError("paragraph IDs and purposes must be nonempty and IDs unique")
        if not isinstance(move["fact_ids"], list) or not move["fact_ids"] or any(not isinstance(x, str) or x not in ids for x in move["fact_ids"]):
            raise ValueError("paragraph plan references missing scientific facts")
        paragraph_ids.add(move["id"])
    placements = brief.get("qualification_placement", [])
    if not isinstance(placements, list):
        raise ValueError("qualification_placement must be a list")
    qualified = set()
    for placement in placements:
        if not isinstance(placement, dict) or set(placement) != {"fact_id", "home", "repeat_when"}:
            raise ValueError("qualification placement requires fact_id/home/repeat_when")
        if not all(isinstance(placement[k], str) and placement[k].strip() for k in placement):
            raise ValueError("qualification placement values must be nonempty text")
        if placement["fact_id"] not in ids or placement["fact_id"] in qualified:
            raise ValueError("qualification must reference one unique scientific fact")
        qualified.add(placement["fact_id"])
    contract = SKILL / "references/scientific-writing-contract.md"
    messages = [{"role": "system", "content": contract.read_text(encoding="utf-8")}]
    dep = dependency(subskill, installed_root) if subskill else None
    if dep and dep["path"]:
        messages.append({"role": "user", "content": "Subordinate advice; apply only within the higher-priority academic profile:\n" + Path(dep["path"]).read_text(encoding="utf-8")})
    task = {"stage": stage, "section_task": section, "scientific_content": clean, "manuscript_brief": brief,
            "output_contract": {"manuscript": "Only revised manuscript text", "notes": "Separate short edit rationale and reverse outline; never concatenate into manuscript", "serialization": "Preserve literal LaTeX backslashes and math delimiters. Use a safe text writer or raw string plus JSON encoder; do not interpret mathematical commands as programming-language escapes. Missing reference details belong in notes and block final bibliography acceptance; never insert retrieval explanations or placeholder references into the manuscript."}}
    if plan:
        task["composition_task"] = "Develop paragraph_plan in reader order: each move adds its stated contribution using fact_ids. The plan describes argument moves, not a fixed paragraph count. In notes map actual paragraphs to moves and identify mergers or deviations."
    if placements:
        task["qualification_task"] = "State each qualification fully at home; repeat locally when repeat_when applies and the nearby claim would otherwise become false or misleading. Else develop the paragraph's new point. Preserve all material scope; placement is not permission to delete it."
    if section_role:
        if section_role not in SECTION_JOBS:
            raise ValueError("unknown section role")
        task["section_job"] = SECTION_JOBS[section_role]
    if source is not None:
        task["current_manuscript"] = source
    if edits is not None:
        for edit in edits:
            if edit.get("action") not in ACTIONS or not all(edit.get(k) for k in ("proposition", "evidence_status", "location", "factual_check")):
                raise ValueError("concern-to-edit requires proposition/status/action/location/factual check")
            if edit["action"] == "BLOCK_EVIDENCE":
                raise ValueError("unresolved evidence blocker cannot become a prose rewrite")
            if edit["evidence_status"] not in STATUSES:
                raise ValueError("edit evidence_status is invalid")
            if "composition" in edit:
                composition = edit["composition"]
                if not isinstance(composition, dict) or set(composition) != {"point", "fact_ids", "preserve"}:
                    raise ValueError("composition requires point/fact_ids/preserve")
                if not isinstance(composition["point"], str) or not composition["point"].strip():
                    raise ValueError("composition requires a scientific point")
                if not isinstance(composition["fact_ids"], list) or not composition["fact_ids"] or any(not isinstance(x, str) or x not in ids for x in composition["fact_ids"]):
                    raise ValueError("composition references missing scientific facts")
                if not isinstance(composition["preserve"], list) or any(not isinstance(x, str) or not x.strip() for x in composition["preserve"]):
                    raise ValueError("composition preserve must list scientific invariants")
        if any(e["action"] == "KEEP" for e in edits) and not all(e["action"] == "KEEP" for e in edits):
            for edit in edits:
                if edit["action"] == "KEEP" and (not edit.get("protected_text") or source is None or source.count(edit["protected_text"]) != 1):
                    raise ValueError("mixed KEEP requires unique protected_text in source")
        # Reviewer dialogue is intentionally not forwarded; only scientific edit decisions.
        task["edits"] = [{k: e[k] for k in ("proposition", "evidence_status", "action", "location", "factual_check")} for e in edits]
        for original, clean_edit in zip(edits, task["edits"]):
            if "composition" in original:
                # Review instructions are output checks, not sentences to paraphrase.
                clean_edit["proposition"] = original["composition"]["point"]
                clean_edit.pop("factual_check")
                clean_edit["supporting_fact_ids"] = original["composition"]["fact_ids"]
                clean_edit["preserve"] = original["composition"]["preserve"]
            if original.get("protected_text"):
                clean_edit["protected_text"] = original["protected_text"]
    if stage in {"P10", "S7"} and source is None:
        raise ValueError("revision requires current manuscript")
    if source is not None and stage in {"P10", "S7", "P19"} and not edits:
        raise ValueError("revision requires concern-to-edit decisions and explicit factual preservation checks")
    messages.append({"role": "user", "content": json.dumps(task, ensure_ascii=False, indent=2)})
    return {"messages": messages, "provenance": {"adapter": "writing_adapter.build/v1", "contract_sha256": sha(contract), "dependency": dep,
            "evidence_manifest": verify, "verification_notes": [{"fact_id": f["id"], "note": f["verification_note"]} for f in facts if f.get("verification_note")],
            "revision_checks": [{k: e[k] for k in ("location", "proposition", "factual_check")} for e in (edits or []) if "composition" in e],
            "model": "unknown", "tool_version": "unknown", "execution": "input-built-only; no model invoked"}}


def response_parts(response, source=None, keep=False, keep_texts=()):
    """Validate the local exchange format without asserting scientific acceptance."""
    if not isinstance(response, dict) or set(response) != {"manuscript", "notes"}:
        raise ValueError("writer response must separate manuscript and notes")
    if not isinstance(response["manuscript"], str) or not response["manuscript"].strip() or not isinstance(response["notes"], str):
        raise ValueError("manuscript must be nonempty text; notes must be separate text")
    if any(ord(c) < 32 and c not in "\t\n\r" for c in response["manuscript"]):
        raise ValueError("manuscript contains control characters; check LaTeX serialization")
    if keep and (source is None or response["manuscript"] != source):
        raise ValueError("KEEP changed manuscript text")
    for protected in keep_texts:
        if not protected or source is None or source.count(protected) != 1 or response["manuscript"].count(protected) != 1:
            raise ValueError("mixed KEEP changed or duplicated protected text")
    return response["manuscript"], response["notes"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--stage", choices=sorted(STAGES), required=True)
    parser.add_argument("--section-task", required=True)
    parser.add_argument("--section-role", choices=sorted(SECTION_JOBS))
    parser.add_argument("--subskill")
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--manuscript", type=Path)
    parser.add_argument("--edits", type=Path)
    parser.add_argument("--response", type=Path, help="validate returned manuscript/notes, without claiming semantic acceptance")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.run_root.resolve()
        if not args.output.resolve().is_relative_to(root):
            raise ValueError("output must be inside run root")
        # Decode bytes directly: universal-newline conversion would violate KEEP.
        source = args.manuscript.read_bytes().decode("utf-8") if args.manuscript else None
        edits = read_json(args.edits) if args.edits else None
        result = build(read_json(args.packet), root, args.stage, args.section_task, args.subskill, args.installed_root, source, edits, args.section_role)
        if args.response:
            manuscript, notes = response_parts(read_json(args.response), source, bool(edits) and all(e["action"] == "KEEP" for e in edits), [e["protected_text"] for e in (edits or []) if e["action"] == "KEEP" and e.get("protected_text")])
            result = {"manuscript": manuscript, "notes": notes, "provenance": result["provenance"], "status": "format-checked; semantic-review-required"}
        result["provenance"]["inputs"] = [{"path": str(p.resolve()), "sha256": sha(p)} for p in (args.packet, args.manuscript, args.edits, args.response) if p]
        save_new(args.output, result)
        print("BUILT: writer messages and separate provenance; generation not executed")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("ERROR:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
