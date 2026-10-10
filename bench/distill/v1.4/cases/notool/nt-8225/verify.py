# DISTILL-CANARY-c1b748e6 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "2 万元" in prompt
assert 20000 * 0.025 == 500
print(json.dumps({"expected_contains_any": ['500 元', '500元', '500 块', '500块']}, ensure_ascii=False))
