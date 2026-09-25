# DISTILL-CANARY-379d227b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kiln_draws_2025_2026.csv"])))
d2026 = [float(r["tonnes"]) for r in rows if r["draw_date"].startswith("2026")]
print(json.dumps({"expected_number": max(d2026)}))
