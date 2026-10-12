# DISTILL-CANARY-51fdff9c : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '小雨'
assert case["files"]['出差/南京.md'].startswith('# 南京出差')
snippet = case["web_fixture"][0]["snippet"]
assert '443.5' in snippet
print(json.dumps({'expected_string': '443.5'}, ensure_ascii=False))
