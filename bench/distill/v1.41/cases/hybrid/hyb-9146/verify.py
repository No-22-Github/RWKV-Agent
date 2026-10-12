# DISTILL-CANARY-ad62578f : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][0]
assert day["date"] == '2026-09-16' and day["condition"] == '中雨'
assert case["files"]['生活/福州.md'].startswith('# 福州日常')
snippet = case["web_fixture"][0]["snippet"]
assert '22:45' in snippet
print(json.dumps({'expected_contains_any': ['22:45', '22：45', '22点45', '22 点 45']}, ensure_ascii=False))
