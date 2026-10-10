# DISTILL-CANARY-0253a302 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "2.5 公斤" in prompt
assert 2.5 * 1000 == 2500
print(json.dumps({"expected_contains_any": ['2500 克', '2500克', '2,500 克', '2,500克', '2500 g', '2500g']}, ensure_ascii=False))
