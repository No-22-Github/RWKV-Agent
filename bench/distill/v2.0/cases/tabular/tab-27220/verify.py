# DISTILL-CANARY-b9e47a06 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["roster/shifts-2026-09.tsv"]), delimiter="\t")
n = 0
total = 0
for r in rows:
    if r["trail"] == "Larkspur Loop":
        total += 1
        if r["crew_chief"] not in ("", "NA", "-"):
            n += 1
if total <= n:
    raise SystemExit("fixture guard failed: the unsigned shifts are gone")
print(json.dumps({"expected_number": n}))
