# DISTILL-CANARY-c0c28f39 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/deck-oven-aug.log"].splitlines() if l.strip()]
alarms = [l for l in lines if " ALARM" in l and "TEST BURN" not in l]
if not alarms:
    raise SystemExit(1)
cause = ""
for line in case["files"]["notes/maintenance.md"].splitlines():
    if line.startswith("Cause:"):
        cause = line[len("Cause:"):].strip().rstrip(".")
if not cause:
    raise SystemExit(1)
facts = [
    "%d over-temp alarms" % len(alarms),
    alarms[0].split()[1],
    cause,
]
print(json.dumps({"expected_contains_any": facts}))
