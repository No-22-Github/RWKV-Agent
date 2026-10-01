# DISTILL-CANARY-ddc044c8 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["beans/menu_2026-10.csv"])))
roasts = sorted(r["roast"] for r in rows)
if roasts != ["中", "浅", "深"]:
    sys.exit("menu no longer carries exactly the three roast levels")
print(json.dumps({"expected_string": "浅烘"}))
