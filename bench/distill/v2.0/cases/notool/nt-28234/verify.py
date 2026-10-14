# DISTILL-CANARY-bc838a79 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "Canada" in prompt
print(json.dumps({"expected_string": 'Ottawa'}, ensure_ascii=False))
