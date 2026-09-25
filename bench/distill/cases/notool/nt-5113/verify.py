# DISTILL-CANARY-10452fef : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["memberships/2026-09-plans.csv"]))
fee = next(r["monthly_gbp"] for r in rows
           if r["plan"] == "Group" and r["term"] == "11 people or more")
print(json.dumps({"expected_number": float(fee)}))
