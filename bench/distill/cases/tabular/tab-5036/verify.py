# DISTILL-CANARY-bc54908f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["collection_log_2025_2026.csv"])))
earlier = [r for r in rows if r["collection_date"].startswith("2025-05")]
later = [r for r in rows if r["collection_date"].startswith("2026-05")]
old = sum(int(r["litres"]) for r in earlier)
new = sum(int(r["litres"]) for r in later)
print(json.dumps({"expected_number": new - old}))
