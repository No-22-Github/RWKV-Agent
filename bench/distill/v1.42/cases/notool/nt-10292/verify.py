# DISTILL-CANARY-ddcbecaa : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["humidity", "wind"]}, ensure_ascii=False))
