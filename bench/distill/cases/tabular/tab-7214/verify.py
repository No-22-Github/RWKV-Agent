# DISTILL-CANARY-219ebfdb : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/peisong-2026-09.csv"]))
tot = {}
for r in rows:
    tot[r["员工编号"]] = tot.get(r["员工编号"], 0) + int(r["桶数"])
ranked = sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))
if ranked[0][1] == ranked[1][1]:
    raise SystemExit("fixture guard failed: tie at the top of the bucket ranking")
print(json.dumps({"expected": ranked[0][0]}))
