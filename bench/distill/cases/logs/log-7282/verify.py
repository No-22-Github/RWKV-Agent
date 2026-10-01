# DISTILL-CANARY-186e3ca1 : distillation case
import csv
import io
import json
case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/vehicle-checks-2026-09.tsv"]), delimiter="\t"))
fieldnames = list(rows[0].keys()) if rows else []
# Positive control: the export carries exactly the five documented columns.
if fieldnames != ["date", "vehicle_id", "route_code", "inspector", "defects"]:
    raise SystemExit("fixture guard failed: check-sheet columns are broken")

# The case premise: no wear measurement column exists anywhere.
if any("wear" in c.lower() or "brake" in c.lower() for c in fieldnames):
    raise SystemExit("fixture has a wear column; the missing-column case is broken")
brake_notes = [r["defects"] for r in rows if "brake pads" in r["defects"]]
if len(brake_notes) != 2:
    raise SystemExit("fixture guard failed: brake text notes are broken")

accepted = ["brake", "wear"]
print(json.dumps({"expected_contains_any": accepted}))
