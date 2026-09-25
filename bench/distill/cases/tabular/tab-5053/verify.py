# DISTILL-CANARY-9267c0fc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["sailings_2026.csv"])))
earlier = [r for r in rows if r["sailing_date"].startswith("2025-06")]
later = [r for r in rows if r["sailing_date"].startswith("2026-06")]
if not earlier:
    print(json.dumps({"expected_string": "UNKNOWN"}))
else:
    old = sum(int(r["vehicles"]) for r in earlier)
    new = sum(int(r["vehicles"]) for r in later)
    print(json.dumps({"expected_number": new - old}))
