# DISTILL-CANARY-e490e6a4 : distillation case
import json
case = json.load(open("case.json"))
path = "logs/weather-log.txt"
before = case["files"][path]
assert before.startswith("2026-09-14 Mon Wuhan") and before.endswith(chr(10))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
line = "%s Thu Wuhan %s %s-%sC" % (day["date"], day["condition"], low, high)
print(json.dumps({"files": {path: before + line + chr(10)}}))
