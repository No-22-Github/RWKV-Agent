# DISTILL-CANARY-2d7d7fb7 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "配置/门店营业.yaml", "start": 7, "end": 9, "new": ["    营业开始: \"10:30\"", "    营业结束: \"20:00\"", "    外卖开关: 关"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
