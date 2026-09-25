# DISTILL-CANARY-df39a606 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["rounds/september-2026.csv"]))
drops = sum(int(row["drops"]) for row in rows)
print(json.dumps({"expected_number": drops}))
