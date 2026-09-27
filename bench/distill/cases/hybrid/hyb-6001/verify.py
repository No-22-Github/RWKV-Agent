# DISTILL-CANARY-7c3a40de : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['cruises/september-2026.csv']))
total = round(sum(float(row['passengers']) for row in rows if row['vessel'] == 'Osprey of Skerray'), 2)
print(json.dumps({"expected_number": total}))
