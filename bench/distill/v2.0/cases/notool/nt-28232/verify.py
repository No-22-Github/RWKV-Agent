# DISTILL-CANARY-eb2924a0 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert round((72 - 32) * 5 / 9, 1) == 22.2
print(json.dumps({"expected_contains_any": ['22.2', '22 °C', '22°C', '22 C', '22 degrees', 'about 22', 'approximately 22']}, ensure_ascii=False))
