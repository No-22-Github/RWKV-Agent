# DISTILL-CANARY-6a614e53 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['周末/天津.md'].startswith('# 天津周末')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
