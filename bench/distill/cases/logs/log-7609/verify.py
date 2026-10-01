# DISTILL-CANARY-7e5f6de4 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/fridge-sep.log"].splitlines() if l.strip()]
excursions = [l for l in lines if "EXCURSION" in l]
recoveries = [l for l in lines if "back in range OK" in l and "DEFROST" not in l]
if not excursions or not recoveries:
    raise SystemExit(1)
note = case["files"]["notes/maintenance.md"]
if "door seal" not in note:
    raise SystemExit(1)
facts = [
    excursions[0].split()[1],
    recoveries[0].split()[1],
    "door seal",
]
print(json.dumps({"expected_contains_any": facts}))
