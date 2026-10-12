# DISTILL-CANARY-c13ee195 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 2
path = "logs/trip-weather.txt"
before = case["files"][path]
assert before.startswith("2026-09-14 Mon Seoul") and before.endswith(chr(10))
tk, os_ = (f["report"]["daily"] for f in case["weather_fixture"])
assert tk[1]["date"] == "2026-09-17" and os_[2]["date"] == "2026-09-18"
def line(d, wd, city):
    low, high = d["temp_c"].split("~")
    return "%s %s %s %s %s-%sC" % (d["date"], wd, city, d["condition"], low, high)
print(json.dumps({"files": {path: before + line(tk[1], "Thu", "Tokyo") + chr(10) + line(os_[2], "Fri", "Osaka") + chr(10)}}))
