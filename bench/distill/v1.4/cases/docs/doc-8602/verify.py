# DISTILL-CANARY-1bb4ef54 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "会议/周会-0914.md", "start": 8, "end": 9, "new": ["- [ ] 魏子轩：对接物流对账，周三前", "- [ ] 邵宇航：更新报价表，下周一前"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
