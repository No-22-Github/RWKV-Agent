# DISTILL-CANARY-93f5a20d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["weighbridge/consignment-book.csv"])))
if not rows:
    raise SystemExit("the weighbridge book is empty")
weights = [int(row["tonnes"]) for row in rows]
heaviest = max(weights)
if weights.count(heaviest) != 1:
    raise SystemExit("the heaviest consignment must be unique")
if heaviest <= min(weights):
    raise SystemExit("the heaviest consignment must beat the lightest one")
print(json.dumps({"expected_number": heaviest}))
