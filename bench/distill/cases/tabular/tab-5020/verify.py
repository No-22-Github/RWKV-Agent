# DISTILL-CANARY-6b1f2a94 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["weighbridge_2026-08.csv"])))
loads = [r for r in rows if r["haulier"] == "Padstow Tippers"]
print(json.dumps({"expected_number": len(loads)}))
