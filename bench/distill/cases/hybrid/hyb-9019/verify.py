# DISTILL-CANARY-3ef17b3a : distillation case
import json
case = json.load(open("case.json"))
rules = case["files"]["site/rules.md"]
assert rules.startswith("# Pour rules") and "40% or more" in rules
day = case["weather_fixture"][0]["report"]["daily"][1]
assert int(day["rain_chance"].rstrip("%")) >= 40
print(json.dumps({"expected_string": day["rain_chance"]}))
