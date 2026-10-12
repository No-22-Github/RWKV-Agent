# DISTILL-CANARY-d6b40e80 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['trip/seoul.md'].startswith('# Seoul trip')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[0])}))
