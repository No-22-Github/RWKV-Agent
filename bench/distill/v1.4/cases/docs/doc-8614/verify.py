# DISTILL-CANARY-b642c141 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "教务/周三课表.md", "start": 7, "end": 8, "new": ["| 第 3 节 | 体育 | 英语 |", "| 第 4 节 | 英语 | 体育 |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
