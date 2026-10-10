# DISTILL-CANARY-da49a590 : distillation case
import json

case = json.load(open("case.json"))
p = case["turns"][0]["prompt"]
assert "18,240" in p and "19,100" in p
print(json.dumps({"expected_number": 18240 * 0.05 - 19100 * 0.04}))
