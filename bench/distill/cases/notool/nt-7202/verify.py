# DISTILL-CANARY-4d29371b : distillation case
import csv
import io
import json
import math

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["parking/exit_2026-10-11.csv"]))
mins = next(float(r["duration_min"]) for r in rows if r["plate"] == "苏E7K90")
print(json.dumps({"expected_number": 6 + math.ceil((mins - 60) / 30) * 2}))
