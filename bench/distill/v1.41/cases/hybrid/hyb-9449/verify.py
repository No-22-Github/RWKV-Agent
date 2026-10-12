# DISTILL-CANARY-465e4293 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == 'Drizzle'
assert case["files"]['trip/seattle.md'].startswith('# Seattle trip')
snippet = case["web_fixture"][0]["snippet"]
assert '$41' in snippet
print(json.dumps({'expected_contains_any': ['$41', '41 dollars', '41 USD', 'USD 41']}, ensure_ascii=False))
