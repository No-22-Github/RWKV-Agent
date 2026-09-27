# DISTILL-CANARY-f4eed36c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["coop_log_2026-06.csv"])))
count = sum(1 for r in rows if r["cracked_eggs"] == "0")
print(json.dumps({"expected_number": count}))
