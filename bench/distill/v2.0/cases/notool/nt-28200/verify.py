# DISTILL-CANARY-8e8ed44b : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "38 箱" in prompt and "24 斤" in prompt
assert 38 * 24 == 912
print(json.dumps({"expected_contains_any": ['912 斤', '912斤']}, ensure_ascii=False))
