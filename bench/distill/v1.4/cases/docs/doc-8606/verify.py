# DISTILL-CANARY-a5ff0d68 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "活动/年会议程.md", "start": 8, "end": 9, "new": ["| 15:50 | 茶歇 | 行政组 |", "| 16:10 | 颁奖典礼 | 工会 |"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
