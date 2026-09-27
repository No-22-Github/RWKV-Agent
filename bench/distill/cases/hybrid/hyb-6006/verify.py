# DISTILL-CANARY-069b3ce5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['baling/april-2026.csv']))
total = round(sum(float(row['bales']) for row in rows if row['farm'] == 'Fernhill Farm' and row['field'] == 'Top Paddock'), 2)
print(json.dumps({"expected_number": total}))
