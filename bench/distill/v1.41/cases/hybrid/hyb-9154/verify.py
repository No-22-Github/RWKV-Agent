# DISTILL-CANARY-80e82ddb : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
assert case["files"]['乐园/票价规定.md'].startswith('# 水上乐园票价规定')
assert case["files"]['乐园/说明.md'].startswith('# 说明')
assert int(day["rain_chance"].rstrip("%")) >= 50 and int(day["temp_c"].split("~")[1]) >= 25
assert 100 * 3 // 2 == 150
print(json.dumps({'expected_string': '150'}, ensure_ascii=False))
