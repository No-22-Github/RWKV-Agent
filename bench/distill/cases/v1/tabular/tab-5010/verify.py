# DISTILL-CANARY-0fa3d8e1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["job_log_2026-07.csv"])))
jobs = {r["job_id"] for r in rows if r["job_id"] != "TOTAL"}
print(json.dumps({"expected_number": len(jobs)}))
