# DISTILL-CANARY-5f44705d : distillation case
import json
case = json.load(open("case.json"))
path = "记录/天气.csv"
before = case["files"][path]
assert before.startswith("date,city,condition,low,high,rain_chance") and before.endswith(chr(10))
assert before.count(chr(10)) == 3
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
row = ",".join([day["date"], "太原", day["condition"], low, high, day["rain_chance"]])
print(json.dumps({"files": {path: before + row + chr(10)}}, ensure_ascii=False))
