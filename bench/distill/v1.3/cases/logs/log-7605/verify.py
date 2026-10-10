# DISTILL-CANARY-87533f19 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/irrigation-jul.log"].splitlines() if l.strip()]
faults = [l for l in lines if "FAULT" in l and "MANUAL TEST" not in l]
shutoff = [l for l in lines if "manual shutoff" in l]
if not faults or not shutoff:
    raise SystemExit(1)
cause = ""
for line in case["files"]["notes/maintenance.md"].splitlines():
    if line.startswith("Cause:"):
        cause = line[len("Cause:"):].strip()
if not cause:
    raise SystemExit(1)
facts = [
    faults[0].split()[1],
    shutoff[0].split()[1],
    "solenoid",
]
print(json.dumps({"expected_contains_any": facts}))
