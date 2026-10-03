# DISTILL-CANARY-986bc4ae : distillation case
import json

case = json.load(open("case.json"))
assert "$86.40" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": 37.5 * 86.40 + 7.5 * 86.40 * 1.5}))
