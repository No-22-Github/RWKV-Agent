# DISTILL-CANARY-9d01999b : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["shipments/declared_2026-10-15.csv"]))
row = next(r for r in rows if r["waybill"] == "ZD-7702")
if row["insured"] != "是":
    sys.exit("ZD-7702 is no longer marked as insured")
print(json.dumps({"expected_number": float(row["declared_cny"]) * 5 / 1000}))
