# DISTILL-CANARY-b6a7deca : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
rules = case["files"]["门店/洗车规则.md"]
assert rules.startswith("# 洗车建议规则") and "两天" in rules and "30%" in rules
assert case["files"]["门店/价目.md"].startswith("# 价目") and "镀膜 280 元" in case["files"]["门店/价目.md"]
assert int(day["rain_chance"].rstrip("%")) >= 30 and int(report["daily"][1]["rain_chance"].rstrip("%")) < 30
print(json.dumps({"expected_string": day["rain_chance"]}))
