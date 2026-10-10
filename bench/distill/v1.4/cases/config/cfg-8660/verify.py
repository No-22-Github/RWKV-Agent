# DISTILL-CANARY-35074c84 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "排班/规则.yaml", "start": 7, "end": 9, "new": ["    开始: \"15:00\"", "    结束: \"23:00\"", "    最少人数: 4"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
