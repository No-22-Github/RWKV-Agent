# DISTILL-CANARY-0509f483 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["depots/parcels_2026-04.csv"])))
per = {}
for r in rows:
    if r["dispatch_date"].startswith("2026-04"):
        per[r["depot"]] = per.get(r["depot"], 0) + int(r["parcels"])
print(json.dumps({"expected_number": max(per.values())}))
