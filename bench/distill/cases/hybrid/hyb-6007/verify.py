# DISTILL-CANARY-b47e10d9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['rides/september-2026.csv']))
count = sum(1 for row in rows if row['pony'] == 'Grey Clover')
print(json.dumps({"expected_number": count}))
