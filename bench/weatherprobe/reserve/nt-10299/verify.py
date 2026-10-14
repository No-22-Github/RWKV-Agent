# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == '南昌'
print(json.dumps({"expected_contains_any": ["立秋", "高温", "炎热"]}, ensure_ascii=False))
