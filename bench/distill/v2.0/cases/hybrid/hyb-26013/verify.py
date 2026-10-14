# DISTILL-CANARY-62e9c517 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['viewings/september-2026.csv']))
count = sum(1 for row in rows if row['flat'] == 'The Garden Flat' and row['address'] == 'Ferndale Road')
print(json.dumps({"expected_number": count}))
