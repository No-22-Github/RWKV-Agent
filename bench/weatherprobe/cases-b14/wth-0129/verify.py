# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == '西安'
print(json.dumps({"expected_contains_any": ["清晨", "日出", "凌晨", "早上"]}, ensure_ascii=False))
