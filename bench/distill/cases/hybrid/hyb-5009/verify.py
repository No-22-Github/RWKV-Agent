# DISTILL-CANARY-0e5b7c81 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["runs/kiln-gas-2026.csv"]))
total = sum(float(row["gas_gbp"]) for row in rows if row["run"] == "Sept-B")
print(json.dumps({"expected_number": round(total, 2)}))
