# DISTILL-CANARY-2d6f8a13 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["survey/block-trees-2026.csv"]))
total = sum(int(row["trees"]) for row in rows)
print(json.dumps({"expected_number": total}))
