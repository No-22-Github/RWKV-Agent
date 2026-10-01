# DISTILL-CANARY-b7d6889a : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["工单导出-2026-08.csv"])))
seen = []
for r in rows:
    tid = r["工单号"].strip()
    if tid not in seen:
        seen.append(tid)
print(json.dumps({"expected_number": len(seen)}))
