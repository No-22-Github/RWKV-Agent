# DISTILL-CANARY-78e501ca : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["crossings/fares-2026-09.csv"]))
fare = next(r["fare_gbp"] for r in rows if r["vehicle_class"] == "Rigid")
print(json.dumps({"expected_number": float(fare)}))
