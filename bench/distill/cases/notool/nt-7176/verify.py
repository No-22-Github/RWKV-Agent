# DISTILL-CANARY-2d678669 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["patterns/seam_allowance.csv"]))
row = next(r for r in rows if r["part"] == "口袋")
num, den = row["allowance_in"].split("/")
print(json.dumps({"expected_number": float(num) / float(den) * 25.4}))
