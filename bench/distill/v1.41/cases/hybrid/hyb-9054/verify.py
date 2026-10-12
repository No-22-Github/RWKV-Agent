# DISTILL-CANARY-28a92c5b : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][0]
assert day["date"] == '2026-09-16'
assert case["files"]['西湖/游览.md'].startswith('# 西湖游览')
print(json.dumps({"expected_string": day["condition"]}))
