# DISTILL-CANARY-4ab225ed : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["takings/ryehill-2026-09.csv"]))
row = next(r for r in rows if r["date"] == "2026-09-17")
print(json.dumps({"expected_number": round(float(row["gross_gbp"]) - float(row["refunds_gbp"]), 2)}))
