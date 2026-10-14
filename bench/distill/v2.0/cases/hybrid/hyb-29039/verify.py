# DISTILL-CANARY-1ca5b251 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['出差/哈尔滨.md'].startswith('# 哈尔滨出差')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[0])}))
