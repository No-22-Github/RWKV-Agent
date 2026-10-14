# DISTILL-CANARY-18b29e1e : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
assert case["files"]['场地/婚礼规定.md'].startswith('# 草坪婚礼场地规定')
assert case["files"]['场地/说明.md'].startswith('# 说明')
assert int(day["temp_c"].split("~")[1]) >= 33 and int(day["rain_chance"].rstrip("%")) < 30
print(json.dumps({'expected_contains_any': ['改室内']}, ensure_ascii=False))
