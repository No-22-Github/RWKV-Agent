# DISTILL-CANARY-3c3830d1 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "ROADMAP.md", "start": 6, "end": 8, "new": ["| Q2 | Offline mode | Mobile |", "| Q3 | Search relevance | Search |", "| Q4 | Billing v2 | Payments, Growth |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
