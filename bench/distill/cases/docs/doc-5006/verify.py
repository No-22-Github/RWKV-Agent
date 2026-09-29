# DISTILL-CANARY-9e05b3da : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["fees/schedule-2026.csv"])))

# Re-run the retrieval: the schedule carries one fee per service, and a service
# it does not list has no fee. A Saturday collection is not one of the listed
# services, and collections.md restricts every collection the laboratory runs
# to working days.
WANTED = "sample collection on a saturday"
match = [r for r in rows if r["service"].strip().lower() == WANTED]
if match:
    raise SystemExit("schedule now lists a Saturday collection; the absent-object case is broken")
for path in sorted(files):
    if "saturday" in files[path].lower():
        raise SystemExit(path + " now mentions a Saturday collection; the absent-object case is broken")
if "working days only" not in files["collections.md"]:
    raise SystemExit("collections.md no longer restricts collections to working days")

accepted = [
    "Saturday collection",
    "saturday collection",
    "collection on a Saturday",
    "Saturday service",
]
print(json.dumps({"expected_contains_any": accepted}))
