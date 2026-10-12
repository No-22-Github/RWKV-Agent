# DISTILL-CANARY-60a1f35f : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][0]
assert day["date"] == '2026-09-16'
assert case["files"]['工作/外勤.md'].startswith('# 外勤安排')
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
