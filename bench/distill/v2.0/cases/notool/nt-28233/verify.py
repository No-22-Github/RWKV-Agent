# DISTILL-CANARY-af9fd196 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert round(9.60 / 12, 2) == 0.80
print(json.dumps({"expected_contains_any": ['0.80', '80 cents', '$0.8']}, ensure_ascii=False))
