# DISTILL-CANARY-adca1af8 : distillation case
import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == 'Dublin'
print(json.dumps({"expected_contains_any": ["30", "chance"]}, ensure_ascii=False))
