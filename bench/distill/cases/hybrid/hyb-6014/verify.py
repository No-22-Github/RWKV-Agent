# DISTILL-CANARY-80ba3e4d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['viewings/june-2026.csv']))
count = sum(1 for row in rows if row['flat'] == 'The Coach House' and row['address'] == 'Harrow Lane')
print(json.dumps({"expected_number": count}))
