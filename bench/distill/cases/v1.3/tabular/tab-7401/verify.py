# DISTILL-CANARY-9c41d2af : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/runs_export.csv"]))
runs = {
    r["run_id"]
    for r in rows
    if r["zone"] == "Docklands" and r["run_month"] == "2026-09"
}
print(json.dumps({"expected_number": len(runs)}))
