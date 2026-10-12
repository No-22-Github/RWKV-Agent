# DISTILL-CANARY-62956f6c : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '雷阵雨'
assert case["files"]['出差/东京.md'].startswith('# 东京出差')
snippet = case["web_fixture"][0]["snippet"]
assert '4.52' in snippet
print(json.dumps({'expected_string': '4.52'}, ensure_ascii=False))
