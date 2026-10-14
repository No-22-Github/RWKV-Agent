# DISTILL-CANARY-8d1b40f6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["claims.csv"])))

# The schedule gives one row per kind of claim; a delivery that arrives short
# is the shortfall row.
wanted = [r for r in rows if r["claim"].strip().lower() == "shortfall on a delivery"]
if not wanted:
    raise SystemExit("the schedule has no row for a shortfall on a delivery")

print(json.dumps({"expected_number": int(wanted[0]["deadline_days"])}))
