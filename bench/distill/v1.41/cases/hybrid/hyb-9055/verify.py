# DISTILL-CANARY-55bd7329 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['火锅/聚餐.md'].startswith('# 重庆聚餐')
print(json.dumps({"expected_string": day["rain_chance"]}))
