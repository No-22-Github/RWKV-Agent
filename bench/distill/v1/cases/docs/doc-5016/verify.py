# DISTILL-CANARY-2b81f9d3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["fees/charges.csv"])))

# Re-run the retrieval. README.md: the sheet lists the firm's standard charges,
# and work it does not list is quoted by the office after a survey. Taking a
# fitted wardrobe down and putting it back together is not one of the listed
# services, and no file in the workspace mentions fitted wardrobe work.
ASKED = "fitted wardrobe disassembly and reassembly"
match = [r for r in rows if r["service"].strip().lower() == ASKED]
if match:
    raise SystemExit("charges sheet now lists fitted wardrobe work; the absent-object case is broken")
for path in sorted(files):
    if "fitted" in files[path].lower():
        raise SystemExit(path + " now mentions fitted wardrobe work; the absent-object case is broken")
if "does not list" not in files["README.md"]:
    raise SystemExit("README.md no longer routes unlisted work to the office survey")

accepted = [
    "fitted wardrobe",
    "fitted wardrobe disassembly and reassembly",
    "taking a fitted wardrobe down",
]
print(json.dumps({"expected_contains_any": accepted}))
