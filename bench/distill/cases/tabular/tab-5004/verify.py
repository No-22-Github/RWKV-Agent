# DISTILL-CANARY-2be6c805 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["loans.csv"])))
hits = [r for r in rows if r["category"] == "garden" and r["loan_date"].startswith("2026-03")]
print(json.dumps({"expected_number": len(hits)}))
