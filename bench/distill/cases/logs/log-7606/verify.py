# DISTILL-CANARY-0c0498da : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/berthing-jun.log"].splitlines() if l.strip()]
suspend = [l for l in lines if "SUSPEND" in l]
if not suspend:
    raise SystemExit(1)
day = suspend[0].split()[0]
faults = [l for l in lines if "FAULT" in l and l.split()[0] == day]
if not faults:
    raise SystemExit(1)
first = faults[0].split()
asset = first[first.index("winch") + 1]
finding = ""
for l in lines:
    if "finding:" in l:
        finding = l.split("finding:")[1].split(" on ")[0].strip()
if not finding:
    raise SystemExit(1)
facts = [
    first[1],
    asset,
    finding,
]
print(json.dumps({"expected_contains_any": facts}))
