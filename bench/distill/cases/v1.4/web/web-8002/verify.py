# DISTILL-CANARY-a9227b9f : distillation case
import json

case = json.load(open("case.json"))
pkg = json.loads(case["files"]["package.json"])
assert pkg["engines"]["node"] == ">=20"
words = ["无法联网", "没法联网", "不能联网", "无法上网", "不能上网", "没有联网", "没有网络", "无法在线", "没法查", "无法查询", "查不了"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
