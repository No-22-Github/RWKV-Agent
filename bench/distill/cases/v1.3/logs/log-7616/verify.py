# DISTILL-CANARY-8997b520 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/water-0812.log"].splitlines() if l.strip()]
alarms = [l for l in lines if "告警" in l]
if not alarms:
    raise SystemExit(1)
parts = alarms[0].split()
note = case["files"]["notes/巡检记录.md"]
if "投药泵" not in note:
    raise SystemExit(1)
facts = [
    "%d 条" % len(alarms),
    parts[2] + " " + parts[3],
    "投药泵",
]
print(json.dumps({"expected_contains_any": facts}))
