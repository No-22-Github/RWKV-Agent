# DISTILL-CANARY-2e11cfde : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["assembly/output_2026-05.csv"])))
seen = set()
per = {}
for r in rows:
    key = (r["batch_id"], r["site"], r["shift"], r["signed_off"], r["units"])
    if key in seen:
        continue
    seen.add(key)
    per[r["site"]] = per.get(r["site"], 0) + int(r["units"])
print(json.dumps({"expected_number": max(per.values())}))
