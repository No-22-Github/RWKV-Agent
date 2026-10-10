# DISTILL-CANARY-63f85c21 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["register/june_intake.csv"]))
rolls = {r["roll_id"] for r in rows
         if "2026-06-08" <= r["intake_date"] <= "2026-06-14"}
print(json.dumps({"expected_number": len(rolls)}))
