# DISTILL-CANARY-b1fd84e6 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['周末/青岛.md'].startswith('# 青岛周末')
print(json.dumps({"expected_string": day["rain_chance"]}))
