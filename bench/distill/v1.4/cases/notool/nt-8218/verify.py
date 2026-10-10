# DISTILL-CANARY-a01a528b : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "周三" in prompt and "100 天" in prompt
assert 100 % 7 == 2
print(json.dumps({"expected_contains_any": ['周五', '星期五']}, ensure_ascii=False))
