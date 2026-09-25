# DISTILL-CANARY-74c8e1b2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["despatch/ashwell-2026-09.csv"]))
cases = sum(int(row["cases"]) for row in rows)
print(json.dumps({"expected_number": cases}))
