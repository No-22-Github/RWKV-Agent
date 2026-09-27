# DISTILL-CANARY-e46b09d7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
out_rows = csv.DictReader(io.StringIO(case["files"]['loads/august-2026.csv']))
ret_rows = csv.DictReader(io.StringIO(case["files"]['empties/august-2026.csv']))
moved = sum(float(row['crates_out']) for row in out_rows if row['van'] == 'Dale Stoat')
back = sum(float(row['crates_returned']) for row in ret_rows if row['van'] == 'Dale Stoat')
print(json.dumps({"expected_number": round(moved - back, 2)}))
