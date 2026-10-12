# DISTILL-CANARY-7bc48fd9 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['学校/运动会规定.md'].startswith('# 运动会举办规定')
assert case["files"]['学校/说明.md'].startswith("# 说明")
assert day['rain_chance']
print(json.dumps({"expected_contains_any": ["延期", "推迟", "改期", "不能"]}, ensure_ascii=False))
