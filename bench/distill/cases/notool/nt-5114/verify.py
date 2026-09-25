# DISTILL-CANARY-77f22baa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["stock/parts-2026-09.csv"]))
free = next(r["available"] for r in rows if r["part"] == "BC-220")
print(json.dumps({"expected_number": int(free)}))
