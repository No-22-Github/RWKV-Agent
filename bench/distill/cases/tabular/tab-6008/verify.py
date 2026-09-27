# DISTILL-CANARY-94f194fc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kilns/firings_2026-07.csv"])))
seen = set()
total = 0.0
for r in rows:
    key = (r["firing_id"], r["kiln"], r["started_date"], r["hours"])
    if key in seen:
        continue
    seen.add(key)
    total += float(r["hours"])
print(json.dumps({"expected_number": round(total, 1)}))
