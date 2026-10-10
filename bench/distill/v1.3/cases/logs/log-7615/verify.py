# DISTILL-CANARY-041e23f4 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/freezer-0918.log"].splitlines() if l.strip()]
alarms = [l for l in lines if "告警" in l]
if not alarms:
    raise SystemExit(1)
cause = ""
for line in case["files"]["notes/维修记录.md"].splitlines():
    if line.startswith("原因："):
        cause = line[len("原因："):].strip()
if "门封条" not in cause:
    raise SystemExit(1)
facts = [
    "%d 次" % len(alarms),
    alarms[0].split()[1],
    "门封条",
]
print(json.dumps({"expected_contains_any": facts}))
