# DISTILL-CANARY-dd641833 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["暖湿", "冷", "凝结"]}, ensure_ascii=False))
