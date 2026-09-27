# DISTILL-CANARY-2a973781 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["consignments_2026-08.csv"])))
total = sum(float(r["amount"].replace("$", "").replace(",", "")) for r in rows)
print(json.dumps({"expected_number": round(total, 2)}))
