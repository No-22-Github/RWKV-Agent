# DISTILL-CANARY-030fb153 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "周五" in prompt and "报告" in prompt
print(json.dumps({"expected_string": '周五'}, ensure_ascii=False))
