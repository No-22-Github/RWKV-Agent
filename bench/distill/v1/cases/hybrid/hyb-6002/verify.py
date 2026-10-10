# DISTILL-CANARY-e2b81d64 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['crossings/august-2026.csv']))
total = round(sum(float(row['vehicles']) for row in rows if row['vessel'] == 'Tern of Sula'), 2)
print(json.dumps({"expected_number": total}))
