# DISTILL-CANARY-6a2f8c14 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["fees/analysis-fees.csv"])))

match = [r for r in rows if r["service"].strip() == "Sieve analysis"]
print(json.dumps({"expected_number": float(match[0]["fee_gbp"])}))
