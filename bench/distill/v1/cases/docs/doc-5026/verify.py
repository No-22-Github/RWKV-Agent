# DISTILL-CANARY-b69e02d7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["periods.csv"])))

# Re-run the retrieval. README.md: the schedule covers kennel bookings; the
# cattery takes its own bookings on a terms sheet held elsewhere, so no row
# here sets the notice for cancelling a cattery place.
wanted = [r for r in rows if "cattery" in r["service"].lower()]
if wanted:
    raise SystemExit("periods.csv now carries a cattery row; the absent-object case is broken")
if "not part of this schedule" not in files["README.md"]:
    raise SystemExit("README.md no longer places the cattery terms outside this schedule")

accepted = [
    "cattery",
    "Cattery",
    "cattery booking",
    "cattery place",
]
print(json.dumps({"expected_contains_any": accepted}))
