# DISTILL-CANARY-3c7a01f2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["extraction/batches-2026-09.csv"]))
premium = sum(1 for row in rows if row["grade"] == "premium")
print(json.dumps({"expected_number": premium}))
