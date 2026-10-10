# DISTILL-CANARY-6b27e5cc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["seedling_trial_june_2026.csv"])))
counts = [int(r["seedlings"]) for r in rows if r["cultivar"] != "TOTAL"]
print(json.dumps({"expected_number": max(counts)}))
