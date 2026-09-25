# DISTILL-CANARY-e9ab5618 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["beet_intake_2026-10.csv"])))
loads = [float(r["tonnes"]) for r in rows if r["grower"] == "Dunragit Farms"]
charge = sum(3.20 * t if t <= 28.0 else 1.60 * t for t in loads)
print(json.dumps({"expected_number": round(charge, 2)}))
