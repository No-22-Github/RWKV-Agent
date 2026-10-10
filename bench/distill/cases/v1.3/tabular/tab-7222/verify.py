# DISTILL-CANARY-0653c556 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/dengji-2026-09.csv"]))
stalls = set()
n_iso = 0
n_dmy = 0
for r in rows:
    if r["交易日期"] == "2026-09-12":
        stalls.add(r["摊位号"])
        n_iso += 1
    elif r["交易日期"] == "12/09/2026":
        stalls.add(r["摊位号"])
        n_dmy += 1
if n_iso < 5 or n_dmy < 5:
    raise SystemExit("fixture guard failed: one date spelling lost its rows")
print(json.dumps({"expected_number": len(stalls)}))
