# DISTILL-CANARY-01d7367a : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18' and day["condition"] == '扬沙'
assert case["files"]['旅行/西北.md'].startswith('# 西北行')
snippet = case["web_fixture"][0]["snippet"]
assert '238' in snippet
print(json.dumps({'expected_string': '238'}, ensure_ascii=False))
