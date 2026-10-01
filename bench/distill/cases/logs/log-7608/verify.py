# DISTILL-CANARY-3d16478d : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/rebalancing-aug.log"].splitlines() if l.strip()]
stockouts = [l for l in lines if "STOCKOUT" in l]
recoveries = [l for l in lines if " OK" in l and "DRILL" not in l]
if not stockouts or not recoveries:
    raise SystemExit(1)
station = ""
for l in stockouts:
    parts = l.split()
    station = " ".join(parts[3:5])
    break
facts = [
    stockouts[0].split()[1],
    recoveries[0].split()[1],
    station,
]
print(json.dumps({"expected_contains_any": facts}))
