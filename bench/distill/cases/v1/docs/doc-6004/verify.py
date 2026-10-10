# DISTILL-CANARY-2f80632f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["terms/booking-terms.csv"])))

# Re-run the retrieval. README.md: terms that are not on the sheet are settled
# directly with the house manager, so the sheet is the complete list of standing
# terms. No row prices a pet, and no file in the workspace mentions one.
match = [r for r in rows if "pet" in r["item"].strip().lower()]
if match:
    raise SystemExit("booking terms now carry a pet row; the absent-object case is broken")
for path in sorted(files):
    if "pet" in files[path].lower():
        raise SystemExit(path + " now mentions a pet charge; the absent-object case is broken")
if "not on the sheet" not in files["README.md"]:
    raise SystemExit("README.md no longer routes unlisted terms to the house manager")

accepted = [
    "pet",
    "pet charge",
    "charge for a pet",
]
print(json.dumps({"expected_contains_any": accepted}))
