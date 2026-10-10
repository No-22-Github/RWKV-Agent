# DISTILL-CANARY-6a3f92c7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["intake/covers-2026-09.csv"])))
if not rows:
    raise SystemExit("the intake log is empty")
damaged = sum(1 for row in rows if row["condition"] == "damaged")
usable = sum(1 for row in rows if row["condition"] == "usable")
assert damaged and usable, "the log must carry both conditions"
assert damaged != usable, "the answer must differ from the other condition's count"
print(json.dumps({"expected_number": damaged}))
