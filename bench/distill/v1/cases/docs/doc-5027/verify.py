# DISTILL-CANARY-24c7f5a8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["periods.csv"])))

# The schedule gives one row per change a customer can ask for; moving a
# booking to another date is its own row.
wanted = [r for r in rows if r["service"].strip().lower() == "moving a booking to another date"]
if not wanted:
    raise SystemExit("the schedule has no row for moving a booking")

print(json.dumps({"expected_number": int(wanted[0]["notice_days"])}))
