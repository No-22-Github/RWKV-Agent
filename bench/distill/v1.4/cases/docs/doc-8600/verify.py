# DISTILL-CANARY-f7be958b : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "docs/打印价目.md", "start": 7, "end": 8, "new": ["| A3 黑白 | 0.90 | 5 |", "| A3 彩色 | 3.50 | 5 |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
