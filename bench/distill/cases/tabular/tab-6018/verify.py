# DISTILL-CANARY-a80ab7ca : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["deliveries_2026-08.csv"])))
_ = sum(int(r["crates"]) for r in rows)
fields = rows[0].keys() if rows else []
if any("damage" in f.lower() for f in fields):
    print(json.dumps({"expected_number": sum(int(r.get("damage_crates", 0) or 0) for r in rows)}))
else:
    print(json.dumps({"expected_string": "UNKNOWN"}))
