# DISTILL-CANARY-09b3f5e1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["intake_2026-08.csv"])))
toll_kg_per_tonne = {"bread wheat": 96.0, "feed wheat": 61.0, "rye": 78.0}
tonnes = {}
for row in rows:
    tonnes[row["grain"]] = tonnes.get(row["grain"], 0.0) + float(row["tonnes"])
toll = sum(tonnes[grain] * toll_kg_per_tonne[grain] for grain in tonnes)
print(json.dumps({"expected_number": round(toll, 1)}))
