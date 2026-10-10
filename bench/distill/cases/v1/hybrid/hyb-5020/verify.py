# DISTILL-CANARY-f5d0a814 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["store/oak-2026.csv"])))
if not rows:
    raise SystemExit("the store card is empty")
boards = sum(int(row["boards"]) for row in rows if row["thickness_mm"] == "32")
other = sum(int(row["boards"]) for row in rows if row["thickness_mm"] != "32")
assert boards and other, "the card must carry both thicknesses"
assert boards != other, "the answer must differ from the other thickness's total"
print(json.dumps({"expected_number": boards}))
