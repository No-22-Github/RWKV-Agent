# DISTILL-CANARY-8e36ad49 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['出差/兰州.md'].startswith('# 兰州出差')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[0])}))
