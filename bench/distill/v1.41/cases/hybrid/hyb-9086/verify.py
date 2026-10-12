# DISTILL-CANARY-48b03f98 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['农场/晾晒规定.md'].startswith('# 稻谷晾晒规定')
assert case["files"]['农场/说明.md'].startswith("# 说明")
assert day['rain_chance']
print(json.dumps({"expected_contains_any": ["不晾晒", "不能", "收进", "收仓", "不晒"]}, ensure_ascii=False))
