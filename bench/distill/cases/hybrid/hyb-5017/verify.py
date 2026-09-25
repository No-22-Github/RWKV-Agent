# DISTILL-CANARY-47e0b3a9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["hire/september-2026.csv"])))
if not rows:
    raise SystemExit("the counter book is empty")
total = sum(int(row["bikes_out"]) for row in rows)
days = int(rows[0]["date"].split("-")[2])
assert total > days, "the answer must be a total over the rows, not a single day"
print(json.dumps({"expected_number": total}))
