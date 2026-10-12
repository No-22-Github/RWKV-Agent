# DISTILL-CANARY-ad22a05b : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
assert case["files"]['club/race-rules.md'].startswith('# Harbour race rules')
assert case["files"]['club/说明.md'].startswith('# README')
assert int(day["temp_c"].split("~")[1]) < 14 and int(day["rain_chance"].rstrip("%")) < 60
print(json.dumps({'expected_contains_any': ['cancelled', 'Cancelled', 'CANCELLED', 'canceled', 'Canceled']}, ensure_ascii=False))
