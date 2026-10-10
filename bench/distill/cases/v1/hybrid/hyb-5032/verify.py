# DISTILL-CANARY-04c8e7b1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["launches/harbour-return-2026-09.csv"])))
if not rows:
    raise SystemExit("the counter book is empty")
counts = [int(row["launches_out"]) for row in rows]
total = sum(counts)
if total == max(counts) or total < max(counts):
    raise SystemExit("the answer must be the September total, not one day")
print(json.dumps({"expected_number": total}))
