# DISTILL-CANARY-280248d9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["products/rate_sheet.csv"]))
row = next(r for r in rows if r["product"] == "稳存二号")
rate = float(row["annual_rate_pct"])
term = float(row["term_years"])
print(json.dumps({"expected_number": 20000 * rate * term / 100}))
