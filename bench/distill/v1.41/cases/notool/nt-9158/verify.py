# DISTILL-CANARY-ac845e02 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
assert case["turns"][0]["expect"]["tools"] == [] and case["turns"][0]["expect"]["require_active_no_call"] is True
print(json.dumps({"expected_contains_any": ["热带风暴", "强台风", "超强台风"]}, ensure_ascii=False))
