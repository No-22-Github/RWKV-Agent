# DISTILL-CANARY-91db2144 : distillation case
import csv
import io
import json
case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/harvest-2026-09.csv"])))
fieldnames = list(rows[0].keys()) if rows else []
# Positive control: the export carries exactly the four documented columns.
if fieldnames != ["date", "hive_id", "frames_harvested", "notes"]:
    raise SystemExit("fixture guard failed: harvest columns are broken")

# The case premise: no weight column exists anywhere.
if any("weight" in c.lower() or "kg" in c.lower() for c in fieldnames):
    raise SystemExit("fixture has a weight column; the missing-column case is broken")
frames = sum(int(r["frames_harvested"]) for r in rows)
if frames != 63:
    raise SystemExit("fixture guard failed: frames decoy total is broken")

accepted = ["weight", "kg", "kilogram"]
print(json.dumps({"expected_contains_any": accepted}))
