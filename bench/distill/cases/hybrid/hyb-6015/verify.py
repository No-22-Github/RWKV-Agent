# DISTILL-CANARY-de70c946 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['readings/september-2026.csv']))
cand = [row for row in rows if row['building'] == 'New Court' and row['meter'] == 'Main']
closing = max(cand, key=lambda row: row['read_date'])
print(json.dumps({"expected_number": float(closing['reading'])}))
