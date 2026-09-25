# DISTILL-CANARY-2c6ad941 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kiln_firings_2026-08.csv"])))
august = [r for r in rows if r["firing_date"].startswith("2026-08")]
try:
    cost = sum(float(r["gas_cost"]) for r in august)
except KeyError:
    print(json.dumps({"expected_string": "UNKNOWN"}))
else:
    print(json.dumps({"expected_number": round(cost, 2)}))
