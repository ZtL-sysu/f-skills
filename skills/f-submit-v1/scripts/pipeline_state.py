#!/usr/bin/env python3
"""Validate ordered workflow evidence; run inside the project's local Conda environment."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def definition():
    return json.loads((Path(__file__).resolve().parents[1] / "assets/pipeline-definition.json").read_text())


def validate(state, root, complete=False, before=None):
    spec = definition()
    errors = []
    if state.get("schema_version") != 1 or state.get("pipeline") != spec["pipeline"]:
        errors.append("wrong schema or pipeline")
    rows = state.get("stages", [])
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return errors + ["stages must be objects in canonical order"]
    if [r.get("id") for r in rows] != spec["stages"]:
        return errors + ["missing, duplicate, extra or reordered stage"]
    version = state.get("contract_version")
    if not isinstance(version, str) or not version.strip():
        errors.append("contract_version required")
    def files_ok(items, label):
        if not isinstance(items, list) or not items:
            errors.append(label + ": nonempty file/hash list required")
            return
        for item in items:
            if not isinstance(item, dict):
                errors.append(label + ": malformed artifact")
                continue
            raw = item.get("path")
            if not isinstance(raw, str) or not raw:
                errors.append(label + ": path required")
                continue
            path = (root / raw).resolve()
            if Path(raw).is_absolute() or not path.is_relative_to(root):
                errors.append(label + ": artifact outside run root")
            elif not path.is_file() or path.stat().st_size == 0:
                errors.append(label + ": missing or empty artifact " + raw)
            elif item.get("sha256") != digest(path):
                errors.append(label + ": stale hash " + raw)
    files_ok(state.get("contract"), "contract")
    gap = False
    for row in rows:
        status = row.get("status")
        if status not in spec["statuses"]:
            errors.append(row["id"] + ": invalid status")
        if status == "passed":
            if gap:
                errors.append(row["id"] + ": predecessor has not passed")
            if row.get("contract_version") != version:
                errors.append(row["id"] + ": stale contract version")
            if row.get("gate_verdict") != "pass":
                errors.append(row["id"] + ": gate verdict must be pass")
            files_ok(row.get("inputs"), row["id"] + " inputs")
            files_ok(row.get("evidence"), row["id"] + " evidence")
        else:
            if gap and status in ("running", "blocked"):
                errors.append(row["id"] + ": work started beyond first unfinished stage")
            gap = True
    if complete and any(r.get("status") != "passed" for r in rows):
        errors.append("delivery requires every stage passed")
    if before is not None:
        if before not in spec["stages"]:
            errors.append("unknown requested stage")
        elif any(r.get("status") != "passed" for r in rows[:spec["stages"].index(before)]):
            errors.append("requested stage has unfinished predecessors")
    events = state.get("history", [])
    if not isinstance(events, list):
        errors.append("history must be a list")
        events = []
    accepted = []
    for event in events:
        if not isinstance(event, dict):
            errors.append("malformed history event")
            continue
        stage = event.get("stage")
        if event.get("action") == "pass":
            if len(accepted) >= len(spec["stages"]) or stage != spec["stages"][len(accepted)]:
                errors.append("history has out-of-order pass")
            else:
                accepted.append(stage)
        elif event.get("action") == "reopen":
            if stage not in spec["stages"] or not isinstance(event.get("reason"), str) or not event["reason"].strip():
                errors.append("reopen requires valid stage and reason")
            elif spec["stages"].index(stage) > len(accepted):
                errors.append("cannot reopen beyond first unfinished stage")
            else:
                accepted = accepted[:spec["stages"].index(stage)]
        else:
            errors.append("unknown history action")
    if accepted != [r["id"] for r in rows if r.get("status") == "passed"]:
        errors.append("history does not match passed stages")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--init", action="store_true", help="create pending ledger, never overwrite")
    parser.add_argument("--complete", action="store_true")
    parser.add_argument("--before", help="require all predecessors passed")
    args = parser.parse_args()
    spec = definition()
    try:
        if args.init:
            state = {"schema_version": 1, "pipeline": spec["pipeline"], "contract_version": "v1",
                     "contract": [], "history": [], "stages": [
                         {"id": stage, "status": "pending", "contract_version": "v1",
                          "inputs": [], "evidence": [], "gate_verdict": "pending"}
                         for stage in spec["stages"]]}
            with args.state.open("x", encoding="utf-8") as stream:
                json.dump(state, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            print("Initialized pending ledger; populate contract files and hashes before execution.")
            return 0
        state = json.loads(args.state.read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("state must be an object")
        errors = validate(state, args.state.resolve().parent, args.complete, args.before)
        if errors:
            for error in errors:
                print("ERROR:", error)
            return 1
        print("PASS: ordered, current evidence; scientific/visual gate judgment remains required.")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("ERROR:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
