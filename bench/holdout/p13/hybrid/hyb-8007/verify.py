# DISTILL-CANARY-185683dc : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["api-usage-2026-09.csv"]))
seen = {}
for r in rows:
    if r["endpoint"].strip() != "image-resize":
        continue
    key = (r["date"].strip(), r["team"].strip(), r["key_type"].strip(), r["calls"].strip())
    seen.setdefault(key, float(r["cost_usd"]))
print(json.dumps({"expected_number": round(sum(seen.values()), 2)}))
