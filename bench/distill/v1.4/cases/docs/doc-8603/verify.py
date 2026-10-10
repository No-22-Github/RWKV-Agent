# DISTILL-CANARY-e37f5fe2 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "SUPPORT.md", "start": 5, "end": 6, "new": ["| 1.8 | end-of-life | 2026-09-30 |", "| 1.9 | maintenance | 2027-01-31 |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
