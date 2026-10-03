# DISTILL-CANARY-e4ea5f05 : distillation case
import json

case = json.load(open("case.json"))
assert "18.9 升" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": int(18.9 / 0.75)}))
