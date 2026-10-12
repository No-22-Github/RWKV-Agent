# DISTILL-CANARY-6868a658 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['出差/成都.md'].startswith('# 成都出差')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
