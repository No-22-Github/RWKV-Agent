# EXAM-CANARY-e9c9beef : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
hc = {}
for l in case["files"]["hr/staff.csv"].splitlines()[1:]:
    _e, team, status = l.split(",")
    if status == "active":
        hc[team] = hc.get(team, 0) + 1
print(json.dumps({"expected_contains_all": [str(v) for v in hc.values()]}))
