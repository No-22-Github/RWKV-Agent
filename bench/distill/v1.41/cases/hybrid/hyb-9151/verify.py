# DISTILL-CANARY-2e14c551 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
assert case["files"]['营地/收费规定.md'].startswith('# 营地收费规定')
assert case["files"]['营地/说明.md'].startswith('# 说明')
low, high = day["temp_c"].split("~")
assert int(low) < 10 and int(day["rain_chance"].rstrip("%")) >= 60
assert 80 // 2 + 50 == 90
print(json.dumps({'expected_string': '90'}, ensure_ascii=False))
