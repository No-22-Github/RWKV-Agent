# DISTILL-CANARY-46b63d6e : distillation case
import json

case = json.load(open("case.json"))
assert "2846 万元" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": round((3217 - 2846) / 2846 * 100, 1)}))
