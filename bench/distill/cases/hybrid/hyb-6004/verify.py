# DISTILL-CANARY-4f5a92bb : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['hires/july-2026.csv']))
total = round(sum(float(row['fee']) for row in rows if row['property'] == 'Hollybank' and row['room'] == 'The Long Gallery'), 2)
print(json.dumps({"expected_number": total}))
