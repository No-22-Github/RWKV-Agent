# DISTILL-CANARY-7f4e5b6d : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][1]
assert day["date"] == '2026-09-17'
assert case["files"]['跑步/计划.md'].startswith('# 秋季跑步计划')
fact = case["web_fixture"][0]["snippet"]
assert '198 元' in fact and day["condition"] == '雷阵雨'
print(json.dumps({"expected_string": day["condition"] + " " + '198'}, ensure_ascii=False))
