# DISTILL-CANARY-71ea26d4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["collection_log_2026.csv"])))
earlier = [r for r in rows if r["collection_date"].startswith("2025-04")]
later = [r for r in rows if r["collection_date"].startswith("2026-04")]
if not earlier:
    print(json.dumps({"expected_string": "UNKNOWN"}))
else:
    old = sum(int(r["litres"]) for r in earlier)
    new = sum(int(r["litres"]) for r in later)
    print(json.dumps({"expected_number": new - old}))
