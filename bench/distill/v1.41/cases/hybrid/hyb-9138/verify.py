# DISTILL-CANARY-d1958f85 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 0
hz, gl = (f["report"]["daily"] for f in case["weather_fixture"])
assert hz[2]["date"] == "2026-09-18" and hz[2]["rain_chance"] == "35%"
assert gl[3]["date"] == "2026-09-19"
print(json.dumps({"expected_number": int(gl[3]["temp_c"].split("~")[1])}))
