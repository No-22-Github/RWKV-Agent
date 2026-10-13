# DISTILL-CANARY-d2908db4 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["闷", "潮"]}, ensure_ascii=False))
