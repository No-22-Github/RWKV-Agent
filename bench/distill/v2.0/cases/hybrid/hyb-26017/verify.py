# DISTILL-CANARY-71f9d2b0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
out_rows = csv.DictReader(io.StringIO(case["files"]['outbound/september-2026.csv']))
ret_rows = csv.DictReader(io.StringIO(case["files"]['returns/september-2026.csv']))
moved = sum(float(row['pallets_out']) for row in out_rows if row['van'] == 'Northgate Badger')
back = sum(float(row['pallets_returned']) for row in ret_rows if row['van'] == 'Northgate Badger')
print(json.dumps({"expected_number": round(moved - back, 2)}))
