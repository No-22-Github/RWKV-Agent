# DISTILL-CANARY-b27c94ef : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["rewinds/bench-book-september.csv"])))
totals = {}
for row in rows:
    totals[row["technician"]] = totals.get(row["technician"], 0) + int(row["units"])
pellows = sorted(name for name in totals if name.endswith("Pellow"))
if len(pellows) != 2:
    raise SystemExit("the book must carry two technicians called Pellow")
answer = totals["Dawn Pellow"]
other = totals["Ivan Pellow"]
assert answer != other, "the two Pellows must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
