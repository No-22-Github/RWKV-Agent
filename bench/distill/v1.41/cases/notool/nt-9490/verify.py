# DISTILL-CANARY-43a75213 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["SIGKILL", "SIGTERM", "强制", "优雅", "清理", "无法捕获", "不能被捕获"]}, ensure_ascii=False))
