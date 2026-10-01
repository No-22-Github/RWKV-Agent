# DISTILL-CANARY-b723eb8f : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/delivery-fees-2026-08.csv"])))
seen = {}
for r in rows:
    seen.setdefault(r["配送单号"].strip(), float(r["配送费(元)"]))
total = round(sum(seen.values()), 2)
print(json.dumps({"expected_number": total}))
