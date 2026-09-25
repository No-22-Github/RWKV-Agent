# DISTILL-CANARY-9e05b3da : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["fees/schedule-2026.csv"])))

# The schedule carries one fee per service; a service it does not list has no fee.
wanted = "sample collection on a saturday"
match = [r for r in rows if r["service"].strip().lower() == wanted]
print(json.dumps({"expected_string": match[0]["fee_gbp"] if match else "UNKNOWN"}))
