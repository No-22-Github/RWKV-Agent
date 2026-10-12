# DISTILL-CANARY-ea6b5589 : distillation case
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == '2026-09-17' and day["condition"] == '阵雨'
assert case["files"]['周末/苏州.md'].startswith('# 苏州半日游')
snippet = case["web_fixture"][0]["snippet"]
assert '16:00' in snippet
print(json.dumps({'expected_contains_any': ['16:00', '16：00', '16点', '16 点', '下午4点', '下午四点', '下午 4 点']}, ensure_ascii=False))
