import csv
import io
import json

case = json.load(open("case.json"))
rosters = [p for p in case["files"]
           if p.endswith("roster.csv") and "/roseburg/" in p]
if len(rosters) != 1:
    raise SystemExit("expected exactly one active-site roster, found %d" % len(rosters))
rows = list(csv.DictReader(io.StringIO(case["files"][rosters[0]])))
leads = [int(row["pager_extension"]) for row in rows if row["role"] == "shift_lead"]
if len(leads) != 1:
    raise SystemExit("expected exactly one shift_lead row, found %d" % len(leads))
print(json.dumps({"expected_number": leads[0]}))
