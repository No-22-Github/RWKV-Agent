# DISTILL-CANARY-89786ceb : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["june-report-final.csv"]))
total = sum(float(r["spend_usd"]) for r in rows)
print(json.dumps({"expected_number": round(total, 2)}))
