# DISTILL-CANARY-0a3565b0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["tanks/stock_list.csv"]))
row = next(r for r in rows if r["tank"] == "R-118")
vol = float(row["length_cm"]) * float(row["width_cm"]) * float(row["height_cm"]) / 1000
print(json.dumps({"expected_number": vol}))
