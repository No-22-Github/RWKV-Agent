# DISTILL-CANARY-34e6dcce : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["splitting_runs_2026-08.csv"])))
runs = [r for r in rows if r["yard"] == "Penrhyddn"]
print(json.dumps({"expected_number": len(runs)}))
