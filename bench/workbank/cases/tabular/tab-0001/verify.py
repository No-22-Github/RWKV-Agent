import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders_june.csv"])))
total = round(sum(float(r["line_total"]) for r in rows), 2)
print(json.dumps({"expected_number": total}))
