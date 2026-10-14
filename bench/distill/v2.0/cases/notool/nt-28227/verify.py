# DISTILL-CANARY-4dfe745b : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert (9 * 60 + 25 + 3 * 60 + 50) == 13 * 60 + 15
print(json.dumps({"expected_contains_any": ['13:15', '1:15 pm', '1:15 PM', '1:15pm', '1:15 p.m.']}, ensure_ascii=False))
