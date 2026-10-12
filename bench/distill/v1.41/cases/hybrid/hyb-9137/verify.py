# DISTILL-CANARY-9e1e6d75 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 0
sh, bj = (f["report"]["daily"] for f in case["weather_fixture"])
assert sh[1]["date"] == "2026-09-17" and bj[2]["date"] == "2026-09-18"
assert sh[1]["temp_c"].split("~")[1] == "31"
print(json.dumps({"expected_number": int(bj[2]["temp_c"].split("~")[1])}))
