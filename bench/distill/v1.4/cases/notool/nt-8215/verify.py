# DISTILL-CANARY-1eaddf11 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "468 元" in prompt
assert 468 / 6 == 78
print(json.dumps({"expected_contains_any": ['78 元', '78元', '78 块', '78块']}, ensure_ascii=False))
