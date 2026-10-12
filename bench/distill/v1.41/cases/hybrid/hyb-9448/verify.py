# DISTILL-CANARY-a2d33314 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == '2026-09-18' and day["condition"] == '阵雨'
assert case["files"]['出差/呼和浩特.md'].startswith('# 呼和浩特出差')
snippet = case["web_fixture"][0]["snippet"]
assert '周一' in snippet
print(json.dumps({'expected_contains_any': ['周一', '星期一', '礼拜一']}, ensure_ascii=False))
