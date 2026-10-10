# DISTILL-CANARY-1b1d101f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["run_log_2026.csv"])))
june = [float(r["area_m2"]) for r in rows if r["run_month"] == "2026-06"]
print(json.dumps({"expected_number": round(sum(june), 1)}))
