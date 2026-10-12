# DISTILL-CANARY-2da3c87d : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['周边/深圳.md'].startswith('# 深圳周末')
print(json.dumps({"expected_string": day["condition"]}))
