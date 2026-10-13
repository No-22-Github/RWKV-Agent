# DISTILL-CANARY-7a659407 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["防晒", "很强", "较强", "高"]}, ensure_ascii=False))
