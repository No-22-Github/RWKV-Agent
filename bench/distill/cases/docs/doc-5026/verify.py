# DISTILL-CANARY-b69e02d7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["periods.csv"])))

# README.md: the schedule covers kennel bookings; the cattery takes its own
# bookings on a terms sheet held elsewhere, so no row here sets the notice for
# cancelling a cattery place.
wanted = [r for r in rows if "cattery" in r["service"].lower()]
print(json.dumps({"expected_string": wanted[0]["notice_days"] if wanted else "UNKNOWN"}))
