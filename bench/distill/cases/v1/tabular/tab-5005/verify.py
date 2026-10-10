# DISTILL-CANARY-c07ef4d6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press_runs.csv"])))
sheets = sum(int(r["sheets_used"]) for r in rows)
print(json.dumps({"expected_number": round(sheets * 0.045, 2)}))
