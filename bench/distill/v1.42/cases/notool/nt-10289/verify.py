# DISTILL-CANARY-c361bcae : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["雷", "闪电"]}, ensure_ascii=False))
