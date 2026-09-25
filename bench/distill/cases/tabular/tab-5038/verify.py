# DISTILL-CANARY-69b3b5ef : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["maintenance_visits_2026-09.csv"])))
visits = [r for r in rows if r["fitter"] == "Marta Delph"]
print(json.dumps({"expected_number": len(visits)}))
