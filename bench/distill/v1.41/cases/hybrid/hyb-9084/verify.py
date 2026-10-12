# DISTILL-CANARY-62d32340 : distillation case
import json
case = json.load(open("case.json"))
path = "行程/周五.md"
before = case["files"][path]
assert before.startswith("# 周五行程") and before.count("天气：（待填）") == 1
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
low, high = day["temp_c"].split("~")
after = before.replace("天气：（待填）", "天气：%s %s~%s°C，降水概率 %s" % (day["condition"], low, high, day["rain_chance"]), 1)
print(json.dumps({"files": {path: after}}, ensure_ascii=False))
