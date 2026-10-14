# DISTILL-CANARY-1398dc09 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "耐心等待" in prompt
print(json.dumps({"expected_string": 'patience'}, ensure_ascii=False))
