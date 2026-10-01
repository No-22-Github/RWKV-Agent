# DISTILL-CANARY-a3f1c2d4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["spec/widths.csv"]))
width_in = next(float(r["width_in"]) for r in rows if r["item"] == "SW-3021")
print(json.dumps({"expected_number": width_in * 2.54}))
