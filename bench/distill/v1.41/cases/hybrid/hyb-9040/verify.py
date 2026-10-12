# DISTILL-CANARY-e7872b1e : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['周边游/昆明.md'].startswith('# 昆明周边游')
print(json.dumps({"expected_string": day["rain_chance"]}))
