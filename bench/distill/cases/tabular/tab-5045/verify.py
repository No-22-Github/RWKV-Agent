# DISTILL-CANARY-52018206 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["hide_intake_2026.csv"])))
cow = [int(r["pieces"]) for r in rows if r["hide_type"] == "Cowhide"]
print(json.dumps({"expected_number": max(cow)}))
