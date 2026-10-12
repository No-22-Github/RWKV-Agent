# DISTILL-CANARY-2db1021e : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == 'Light rain'
assert case["files"]['trip/japan.md'].startswith('# Japan trip')
snippet = case["web_fixture"][0]["snippet"]
assert '14,720' in snippet
print(json.dumps({'expected_string': '14,720'}, ensure_ascii=False))
