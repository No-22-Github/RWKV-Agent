# DISTILL-CANARY-8d53f03e : distillation case
import json

case = json.load(open("case.json"))
assert "350 kW" in case["turns"][0]["prompt"] and "3.517 kW" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": round(350 / 3.517, 2)}))
