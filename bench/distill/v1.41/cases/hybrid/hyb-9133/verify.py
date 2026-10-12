# DISTILL-CANARY-22e5e29b : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 4
path = "行程/明日.md"
rows = case["files"][path].splitlines()
assert rows == ["# 明日出行", "", "- 地点：杭州", "- 天气：（待填）"]
hz, sz = (f["report"]["daily"][1] for f in case["weather_fixture"])
assert hz["date"] == "2026-09-17" and sz["date"] == "2026-09-17"
low, high = sz["temp_c"].split("~")
rows[2] = "- 地点：苏州"
rows[3] = "- 天气：%s %s~%s°C，降水概率 %s" % (sz["condition"], low, high, sz["rain_chance"])
print(json.dumps({"files": {path: chr(10).join(rows) + chr(10)}}, ensure_ascii=False))
