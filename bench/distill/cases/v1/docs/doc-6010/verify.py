# DISTILL-CANARY-2378bc1b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["warranty/cover.csv"])))

# Re-run the retrieval. README.md: the sheet covers manufacture faults only;
# accidental damage is sold separately under the Yarwell Care plan and never
# appears on the cover sheet. The dishwasher row carries parts and labour
# years and no damage term of its own. (README.md names accidental damage in
# that rule, so the absence check is scoped to the cover sheet itself.)
wanted = [r for r in rows if r["model"].strip().lower() == "dishwasher"]
if not wanted:
    raise SystemExit("cover sheet lost its dishwasher row; fixture does not match the case")
for row in rows:
    if "accidental" in " ".join(str(v) for v in row.values()).lower() or any(
        "accidental" in (k or "").lower() for k in row
    ):
        raise SystemExit("cover sheet now carries an accidental damage term; the absent-object case is broken")
if "never appears on the cover sheet" not in files["README.md"]:
    raise SystemExit("README.md no longer excludes accidental damage from the cover sheet")

accepted = [
    "accidental damage",
    "Accidental damage",
    "accidental damage cover",
]
print(json.dumps({"expected_contains_any": accepted}))
