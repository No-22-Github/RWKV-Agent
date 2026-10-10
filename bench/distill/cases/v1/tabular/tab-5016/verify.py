# DISTILL-CANARY-1cf5b8d0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["flour_deliveries_2026-08.csv"])))
totals = {}
seen = set()
for row in rows:
    if row["note_id"] in seen:
        continue
    seen.add(row["note_id"])
    totals[row["supplier"]] = totals.get(row["supplier"], 0) + int(row["sacks"])
content = "supplier,sacks\n" + "\n".join(
    "%s,%d" % (name, totals[name]) for name in sorted(totals)) + "\n"
print(json.dumps({"files": {"reports/supplier_totals.csv": content}}))
