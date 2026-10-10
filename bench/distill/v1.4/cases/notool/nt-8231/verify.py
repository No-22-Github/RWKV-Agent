# DISTILL-CANARY-f50aa693 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "committee approved" in prompt
print(json.dumps({"expected_string": 'was approved'}, ensure_ascii=False))
