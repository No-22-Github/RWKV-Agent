# DISTILL-CANARY-737b96dc : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert case["files"]['园务/春秋游规定.md'].startswith('# 幼儿园春秋游规定')
assert day['rain_chance']
print(json.dumps({"expected_contains_any": ["取消", "改期", "不能"]}, ensure_ascii=False))
