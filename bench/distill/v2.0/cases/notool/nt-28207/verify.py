# DISTILL-CANARY-8c29730f : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "5.4 米" in prompt and "3.5 米" in prompt
assert round(5.4 * 3.5, 1) == 18.9
print(json.dumps({"expected_contains_any": ['18.9']}, ensure_ascii=False))
