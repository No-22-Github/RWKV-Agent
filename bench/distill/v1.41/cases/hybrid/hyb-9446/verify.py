# DISTILL-CANARY-56b6af3c : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '雷阵雨'
assert case["files"]['旅行/洛阳.md'].startswith('# 洛阳行')
snippet = case["web_fixture"][0]["snippet"]
assert '90' in snippet
print(json.dumps({'expected_string': '90'}, ensure_ascii=False))
