# DISTILL-CANARY-0fbdc601 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["haulage/lane-rates-2026-09.csv"]))
rate = next(r["rate_per_pallet_gbp"] for r in rows
            if r["lane"] == "Aberdeen" and r["carrier"] == "Northline")
print(json.dumps({"expected_number": float(rate)}))
