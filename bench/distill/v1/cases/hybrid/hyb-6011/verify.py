# DISTILL-CANARY-cf51b8e3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['journeys/september-2026.csv']))
total = round(sum(float(row['miles']) for row in rows if row['bus'] == 'Grey Wren'), 2)
print(json.dumps({"expected_number": total}))
