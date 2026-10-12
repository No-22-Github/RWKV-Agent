# DISTILL-CANARY-20037fe0 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['trip/xian.md'].startswith("# Xi'an trip")
print(json.dumps({"expected_string": day["rain_chance"]}))
