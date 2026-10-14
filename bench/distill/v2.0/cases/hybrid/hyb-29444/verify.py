# DISTILL-CANARY-9c476fee : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '阵雨'
assert case["files"]['旅行/厦门.md'].startswith('# 厦门行')
snippet = case["web_fixture"][0]["snippet"]
assert '35' in snippet
print(json.dumps({'expected_string': '35'}, ensure_ascii=False))
