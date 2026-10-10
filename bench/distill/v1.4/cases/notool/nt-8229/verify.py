# DISTILL-CANARY-0abe6d8d : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert 3.5 * 1000 == 3500
print(json.dumps({"expected_contains_any": ['3500', '3,500']}, ensure_ascii=False))
