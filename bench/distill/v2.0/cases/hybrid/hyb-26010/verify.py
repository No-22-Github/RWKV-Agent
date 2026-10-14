# DISTILL-CANARY-3a97d40b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['bakes/july-2026.csv']))
count = sum(1 for row in rows if row['baker'] == 'Tomas Brierley')
print(json.dumps({"expected_number": count}))
