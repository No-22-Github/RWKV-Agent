# DISTILL-CANARY-849264b2 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/cabinet-0614.log"].splitlines() if l.strip()]
faults = [l for l in lines if "故障" in l and "演练" not in l]
recoveries = [l for l in lines if "恢复" in l and "演练" not in l]
if not faults or not recoveries:
    raise SystemExit(1)
note = case["files"]["notes/运维记录.md"]
if "锁扣电机" not in note:
    raise SystemExit(1)
facts = [
    faults[0].split()[1],
    recoveries[0].split()[1],
    "锁扣电机",
]
print(json.dumps({"expected_contains_any": facts}))
