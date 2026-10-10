# DISTILL-CANARY-ddcf294a : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "光合作用" in prompt
print(json.dumps({"expected_contains_any": ['二氧化碳', 'CO2', 'CO₂']}, ensure_ascii=False))
