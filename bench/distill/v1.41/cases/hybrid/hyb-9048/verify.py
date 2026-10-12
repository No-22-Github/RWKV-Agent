# DISTILL-CANARY-3e479d4b : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
rules = case["files"]["规则/户外活动.md"]
assert rules.startswith("# 户外活动规则") and "33°C" in rules and "50%" in rules
assert case["files"]["规则/说明.md"].startswith("# 说明")
assert int(day["temp_c"].split("~")[1]) >= 33 and int(day["rain_chance"].rstrip("%")) < 50
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
