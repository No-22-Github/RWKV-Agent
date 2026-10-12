# DISTILL-CANARY-1e4c87f6 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["吹来", "来自", "来的方向", "从西北", "风速", "蒲福"]}, ensure_ascii=False))
