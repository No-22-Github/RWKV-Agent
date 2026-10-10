# DISTILL-CANARY-0277f041 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "42.195" in prompt
assert round(42.195 / 1.609344, 1) == 26.2
print(json.dumps({"expected_contains_any": ['26.2']}, ensure_ascii=False))
