# DISTILL-CANARY-a664ef7f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["maintenance/service-schedule.csv"])))

# Re-run the retrieval. README.md: a part with no row in the schedule has no
# fixed interval and is inspected by the fitters each service instead. No row
# in the schedule names brake fluid; the winter checklist only tests the fluid
# for moisture at depot visits, which is not a mileage cycle.
ASKED = "brake fluid"
match = [r for r in rows if ASKED in r["component"].strip().lower()]
if match:
    raise SystemExit("service schedule now lists brake fluid; the absent-object case is broken")
if ASKED in files["maintenance/service-schedule.csv"].lower():
    raise SystemExit("service schedule now mentions brake fluid; the absent-object case is broken")
if "no row in the schedule" not in files["README.md"]:
    raise SystemExit("README.md no longer states the no-fixed-interval rule")

accepted = [
    "brake fluid",
    "brake-fluid",
    "brake fluid flush",
]
print(json.dumps({"expected_contains_any": accepted}))
