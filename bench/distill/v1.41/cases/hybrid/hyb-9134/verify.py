# DISTILL-CANARY-18543fd8 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 7
path = "运动/跑步计划.md"
rows = case["files"][path].splitlines()
assert rows == ["# 跑步计划", "", "## 周四 成都", "- 天气：（待填）", "", "## 备注", "- 目标配速 6:00"]
cd, cq = (f["report"]["daily"] for f in case["weather_fixture"])
assert cd[1]["date"] == "2026-09-17" and cq[2]["date"] == "2026-09-18"
day = cq[2]
low, high = day["temp_c"].split("~")
rows[2] = "## 周五 重庆"
rows[3] = "- 天气：%s %s~%s°C，降水概率 %s" % (day["condition"], low, high, day["rain_chance"])
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
