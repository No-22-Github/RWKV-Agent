# DISTILL-CANARY-d19a5d6e : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "运维/备份计划.ini", "start": 8, "end": 10, "new": ["周期 = 每周", "时间 = 01:45", "保留份数 = 10"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
