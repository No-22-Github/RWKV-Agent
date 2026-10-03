# DISTILL-CANARY-99b048a2 : distillation case
import json

case = json.load(open("case.json"))
src = case["turns"][0]["prompt"].split(": ", 1)[1]
assert "18:00" in src and "22:00" in src and "周五" in src
print(json.dumps({"expected_contains_any": ["maintenance"]}))
