# DISTILL-CANARY-0aa95857 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert 0.15 * 240 == 36.0
print(json.dumps({"expected_number": 36}))
