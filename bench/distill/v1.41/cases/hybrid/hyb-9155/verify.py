# DISTILL-CANARY-e6f9288c : distillation case
import json
case = json.load(open("case.json"))
path = "数据/forecast.json"
before = case["files"][path]
assert before.startswith('{"city":"克拉玛依"') and before.endswith(chr(10)) and before.count(chr(10)) == 1
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
text = '{"city":"乌鲁木齐","date":"%s","condition":"%s","low":%s,"high":%s}' % (day["date"], day["condition"], low, high) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
