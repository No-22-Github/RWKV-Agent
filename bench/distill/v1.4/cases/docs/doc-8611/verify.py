# DISTILL-CANARY-856fa713 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "docs/adr/decisions.md", "start": 3, "end": 6, "new": ["- Status: accepted", "- Date: 2026-09-10", "- Deciders: platform team, SRE", "- Supersedes: ADR-009"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
