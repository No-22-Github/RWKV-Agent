# DISTILL-CANARY-7b3159e7 : distillation case
import json
case = json.load(open("case.json"))
for path, text in case["files"].items():
    assert text.startswith('# 旅行清单'), path
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
print(json.dumps({"expected_string": day["rain_chance"]}))
