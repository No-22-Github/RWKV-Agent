# DISTILL-CANARY-4eb0b018 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["handbook/entitlements.csv"])))

# Re-run the retrieval. README.md: the handbook grants exactly what the table
# lists; anything beyond it is agreed case by case with a director and never
# counts as standard. No sabbatical row exists, and no file in the workspace
# mentions one.
WANTED = "sabbatical"
match = [r for r in rows if WANTED in r["entitlement"].strip().lower()]
if match:
    raise SystemExit("entitlements table now lists a sabbatical; the absent-object case is broken")
for path in sorted(files):
    if WANTED in files[path].lower():
        raise SystemExit(path + " now mentions a sabbatical; the absent-object case is broken")
if "grants exactly what the table lists" not in files["README.md"]:
    raise SystemExit("README.md no longer states the closed-grant rule")

accepted = [
    "sabbatical",
    "Sabbatical",
    "sabbatical leave",
]
print(json.dumps({"expected_contains_any": accepted}))
