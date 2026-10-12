# DISTILL-CANARY-0bfe4af0 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][0]
assert day["date"] == '2026-09-16' and day["condition"] == '雷阵雨'
assert case["files"]['生活/广州.md'].startswith('# 广州周末')
snippet = case["web_fixture"][0]["snippet"]
assert '150' in snippet
print(json.dumps({'expected_string': '150'}, ensure_ascii=False))
