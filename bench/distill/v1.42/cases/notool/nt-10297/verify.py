# DISTILL-CANARY-5ab60e8d : distillation case
import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == '广州'
print(json.dumps({"expected_contains_any": ["不一定", "不等于"]}, ensure_ascii=False))
