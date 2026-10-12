# DISTILL-CANARY-ecbcac0f : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18' and day["condition"] == '大雨'
assert case["files"]['旅行/海南.md'].startswith('# 海南行')
snippet = case["web_fixture"][0]["snippet"]
assert '79.5' in snippet
print(json.dumps({'expected_string': '79.5'}, ensure_ascii=False))
