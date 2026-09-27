# DISTILL-CANARY-971629ee : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press/runs_2026-08.csv"])))
runs = set()
for r in rows:
    if r["client"] == "Dunwich Academy":
        runs.add(r["run_id"])
print(json.dumps({"expected_number": len(runs)}))
