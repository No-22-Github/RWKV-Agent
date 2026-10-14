# DISTILL-CANARY-26b78a30 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "周三" in prompt
print(json.dumps({"expected_string": 'Wednesday'}, ensure_ascii=False))
