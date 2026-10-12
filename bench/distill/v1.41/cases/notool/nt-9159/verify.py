# DISTILL-CANARY-68f9fffa : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
assert case["turns"][0]["expect"]["tools"] == [] and case["turns"][0]["expect"]["require_active_no_call"] is True
print(json.dumps({"expected_contains_any": ["long-term", "long term", "decades", "30 years", "average"]}, ensure_ascii=False))
