# DISTILL-CANARY-18e5e042 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/raingauge-0621.log"].splitlines() if l.strip()]
gaps = [l for l in lines if "缺测" in l and "检修" not in l]
recoveries = [l for l in lines if "恢复" in l and "检修" not in l]
if not gaps or not recoveries:
    raise SystemExit(1)
note = case["files"]["notes/值班记录.md"]
if "电池" not in note:
    raise SystemExit(1)
facts = [
    gaps[0].split()[1],
    recoveries[0].split()[1],
    "电池",
]
print(json.dumps({"expected_contains_any": facts}))
