# DISTILL-CANARY-5ccf34fb : distillation case
import json
case = json.load(open("case.json"))
for path, text in case["files"].items():
    assert text.startswith('# 出差行程'), path
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
