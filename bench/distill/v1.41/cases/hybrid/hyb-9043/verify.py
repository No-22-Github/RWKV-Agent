# DISTILL-CANARY-5007c8bf : distillation case
import json
case = json.load(open("case.json"))
path = "出行/周末.md"
before = case["files"][path]
assert before.startswith("# 周末出行") and before.count("天气：（待填）") == 2
nj, yz = (f["report"]["daily"] for f in case["weather_fixture"])
assert nj[3]["date"] == "2026-09-19" and yz[4]["date"] == "2026-09-20"
def fmt(d):
    low, high = d["temp_c"].split("~")
    return "天气：%s %s~%s°C，降水概率 %s" % (d["condition"], low, high, d["rain_chance"])
after = before.replace("天气：（待填）", fmt(nj[3]), 1).replace("天气：（待填）", fmt(yz[4]), 1)
print(json.dumps({"files": {path: after}}, ensure_ascii=False))
