# DISTILL-CANARY-6610519d : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "closest" in prompt
print(json.dumps({"expected_string": 'Mercury'}, ensure_ascii=False))
