# DISTILL-CANARY-09ecab3a : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["上升", "下沉", "冷却", "凝结", "辐合", "辐散"]}, ensure_ascii=False))
