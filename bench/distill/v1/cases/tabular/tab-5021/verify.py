# DISTILL-CANARY-0d7c53be : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["weighbridge_2026-09.csv"])))
tonnes = [float(r["tonnes"]) for r in rows if r["stone_grade"] == "G-10"]
print(json.dumps({"expected_number": round(sum(tonnes), 1)}))
