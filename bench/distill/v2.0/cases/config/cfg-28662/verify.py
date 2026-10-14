# DISTILL-CANARY-14b6e9cc : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "配置/会员档.ini", "start": 7, "end": 9, "new": ["月费 = 99", "折扣 = 0.88", "赠券张数 = 6"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
