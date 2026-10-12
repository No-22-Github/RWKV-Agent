# DISTILL-CANARY-0e0b038a : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['工地/浇筑规程.md'].startswith('# 混凝土浇筑规程')
assert day['temp_c']
print(json.dumps({"expected_contains_any": ["暂停", "改期", "不能"]}, ensure_ascii=False))
