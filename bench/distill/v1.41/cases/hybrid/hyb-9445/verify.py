# DISTILL-CANARY-91e3808f : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == 'Light rain'
assert case["files"]['trip/uk.md'].startswith('# UK trip')
snippet = case["web_fixture"][0]["snippet"]
assert '£25' in snippet
print(json.dumps({'expected_contains_any': ['£25', '25 pounds', 'GBP 25', '25 GBP']}, ensure_ascii=False))
