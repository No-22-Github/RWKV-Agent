# DISTILL-CANARY-91de4c07 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['hires/august-2026.csv']))
count = sum(1 for row in rows if row['venue'] == 'Cove Street' and row['room'] == 'The Sail Loft')
print(json.dumps({"expected_number": count}))
