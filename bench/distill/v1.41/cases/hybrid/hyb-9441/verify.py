# DISTILL-CANARY-3378455d : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '小雨'
assert case["files"]['旅行/成都.md'].startswith('# 成都行')
snippet = case["web_fixture"][0]["snippet"]
assert '7:30' in snippet
print(json.dumps({'expected_contains_any': ['7:30', '7：30', '7点30', '7 点 30', '7点半', '七点半']}, ensure_ascii=False))
