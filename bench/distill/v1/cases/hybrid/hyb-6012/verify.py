# DISTILL-CANARY-a0d47f92 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['runs/april-2026.csv']))
total = round(sum(float(row['drops']) for row in rows if row['van'] == 'White Lark'), 2)
print(json.dumps({"expected_number": total}))
