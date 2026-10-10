# DISTILL-CANARY-45de4544 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["wash/Aug-2026-line-A.csv"])))
b = list(csv.DictReader(io.StringIO(files["wash/Aug-2026-line-B.csv"])))
assert a and set(a[0]) == {"cycle_id", "date", "program", "weight_kg"}
assert b and set(b[0]) == {"cycle_id", "date", "program", "weight_kg"}
assert max(r["date"] for r in b) <= "2026-08-18"
print(json.dumps({"expected_number": len(a)}))
