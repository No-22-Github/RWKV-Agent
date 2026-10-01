# DISTILL-CANARY-7a1bca60 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/dock_events.tsv"]), delimiter="	")
seen = set()
for r in rows:
    if r["event_month"] == "2026-04" and r["tier"] == "Electric":
        seen.add(r["bike_id"])
print(json.dumps({"expected_number": len(seen)}))
