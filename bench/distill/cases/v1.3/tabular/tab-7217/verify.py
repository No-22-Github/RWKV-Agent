# DISTILL-CANARY-5b9d995f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/entries-2026-09.csv"]))
n = 0
n_iso = 0
n_mdy = 0
for r in rows:
    if r["entry_date"] == "2026-09-18":
        n_iso += 1
    elif r["entry_date"] == "09/18/2026":
        n_mdy += 1
if n_iso < 5 or n_mdy < 5:
    raise SystemExit("fixture guard failed: one date spelling lost its rows")
print(json.dumps({"expected_number": n_iso + n_mdy}))
