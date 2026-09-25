# DISTILL-CANARY-92f6c047 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["extraction/september-2026.csv"])))
block_rows = [row for row in rows if row["block"] == "Block 7"]
quarries = {row["quarry"] for row in block_rows}
if len(quarries) != 2:
    raise SystemExit("two quarries must work a face called Block 7")
answer = sum(1 for row in block_rows if row["quarry"] == "Barrowcliff")
other = sum(1 for row in block_rows if row["quarry"] != "Barrowcliff")
assert answer != other, "the two Block 7 faces must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
