# DISTILL-CANARY-5b1e92c4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["picks/september-2026.csv"]))
crates = sum(int(row["crates"]) for row in rows if row["block"] == "Ridgeway South")
print(json.dumps({"expected_number": crates}))
