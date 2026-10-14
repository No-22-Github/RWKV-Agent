# DISTILL-CANARY-c82541fa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
out_rows = csv.DictReader(io.StringIO(case["files"]['generation/september-2026.csv']))
ret_rows = csv.DictReader(io.StringIO(case["files"]['curtailment/september-2026.csv']))
moved = sum(float(row['kwh']) for row in out_rows if row['array'] == 'Turf Fen Array')
back = sum(float(row['kwh']) for row in ret_rows if row['array'] == 'Turf Fen Array')
print(json.dumps({"expected_number": round(moved - back, 2)}))
