# DISTILL-CANARY-f13b7a08 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
out_rows = csv.DictReader(io.StringIO(case["files"]['output/august-2026.csv']))
ret_rows = csv.DictReader(io.StringIO(case["files"]['spill/august-2026.csv']))
moved = sum(float(row['kwh']) for row in out_rows if row['array'] == 'Orchard End Array')
back = sum(float(row['kwh']) for row in ret_rows if row['array'] == 'Orchard End Array')
print(json.dumps({"expected_number": round(moved - back, 2)}))
