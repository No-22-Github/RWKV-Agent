# DISTILL-CANARY-9d8a70c7 : distillation case
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][2]
assert day["date"] == '2026-09-18'
assert case["files"]["旅行/大理.md"].startswith("# 大理行")
assert all("洱海" not in a for a in case["weather_fixture"][0]["aliases"]) and "洱海" not in report["location"]
print(json.dumps({"expected_number": int(day["temp_c"].split("~")[1])}))
