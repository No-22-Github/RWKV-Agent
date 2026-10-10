# DISTILL-CANARY-ed6ba7bd : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "值班/国庆.md", "start": 6, "end": 7, "new": ["| 10-02 | 柴雪晴 | 容嘉树 |", "| 10-03 | 容嘉树 | 柴雪晴 |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
