# DISTILL-CANARY-e352edc2 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18' and day["condition"] == '大雨'
assert case["files"]['旅行/西安.md'].startswith('# 西安行')
snippet = case["web_fixture"][0]["snippet"]
assert '120' in snippet
print(json.dumps({'expected_string': '120'}, ensure_ascii=False))
