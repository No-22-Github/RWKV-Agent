# DISTILL-CANARY-c1cfdd31 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["waybills/pickup_2026-10-09.csv"]))
row = next(r for r in rows if r["waybill"] == "YD-7713")
vol = float(row["length_cm"]) * float(row["width_cm"]) * float(row["height_cm"]) / 6000
print(json.dumps({"expected_number": max(vol, float(row["actual_kg"]))}))
