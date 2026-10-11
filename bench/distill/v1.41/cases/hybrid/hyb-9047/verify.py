# DISTILL-CANARY-fb295125 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]['出游/张家界.md'].startswith('# 张家界两日游')
fact = case["web_fixture"][0]["snippet"]
assert '1 小时 59 分' in fact and day["condition"] == '中雨'
print(json.dumps({"expected_string": day["condition"] + " " + '59'}, ensure_ascii=False))
