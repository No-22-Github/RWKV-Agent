# DISTILL-CANARY-3d8217ab : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["collection_log_2025_2026.csv"])))
seen = set()
old = 0
new = 0
for row in rows:
    if row["collection_date"].startswith("2025-03"):
        old += int(row["litres"])
    elif row["collection_date"].startswith("2026-03") and row["collection_id"] not in seen:
        seen.add(row["collection_id"])
        new += int(row["litres"])
print(json.dumps({"expected_number": new - old}))
