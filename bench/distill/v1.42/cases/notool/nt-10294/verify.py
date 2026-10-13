# DISTILL-CANARY-48d68d62 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["radiat", "heat"]}, ensure_ascii=False))
