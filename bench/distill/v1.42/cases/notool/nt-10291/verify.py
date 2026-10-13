# DISTILL-CANARY-ebcdb4a2 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["红色", "蓝色"]}, ensure_ascii=False))
