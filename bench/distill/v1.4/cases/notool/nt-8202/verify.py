# DISTILL-CANARY-99480800 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "90 公里" in prompt and "2.5 小时" in prompt
assert 90 * 2.5 == 225
print(json.dumps({"expected_contains_any": ['225 公里', '225公里', '225 km', '225km', '225 千米', '225千米']}, ensure_ascii=False))
