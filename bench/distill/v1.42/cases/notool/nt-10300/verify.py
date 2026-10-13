# DISTILL-CANARY-449e0348 : distillation case
import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == '合肥'
print(json.dumps({"expected_contains_any": ["先", "转"]}, ensure_ascii=False))
