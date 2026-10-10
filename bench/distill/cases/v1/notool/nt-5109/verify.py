# DISTILL-CANARY-965e791f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["gate-fees/tariff-2026-09.csv"]))
fee = next(r["gate_fee_gbp"] for r in rows
           if r["category"] == "Soil and rubble" and r["band"] == "over 6 t")
print(json.dumps({"expected_number": float(fee)}))
