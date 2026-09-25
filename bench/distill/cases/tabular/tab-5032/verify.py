# DISTILL-CANARY-5f16e3a9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["braiding_log_2026-06.csv"])))
runs = {r["run_id"] for r in rows if r["run_id"] != "TOTAL"}
print(json.dumps({"expected_number": len(runs)}))
