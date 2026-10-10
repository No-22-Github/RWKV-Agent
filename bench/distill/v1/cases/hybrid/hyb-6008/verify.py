# DISTILL-CANARY-5e8f26a1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['treks/march-2026.csv']))
total = round(sum(float(row['hours']) for row in rows if row['horse'] == 'Little Bramble'), 2)
print(json.dumps({"expected_number": total}))
