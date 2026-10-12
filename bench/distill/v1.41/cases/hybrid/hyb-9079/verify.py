# DISTILL-CANARY-f3ca73fb : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['trip/sydney.md'].startswith('# Sydney trip')
print(json.dumps({"expected_string": day["rain_chance"]}))
