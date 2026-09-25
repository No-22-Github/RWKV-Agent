# DISTILL-CANARY-5af38d16 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["picking/packhouse-sheet-september.csv"])))
totals = {}
for row in rows:
    totals[row["plot"]] = totals.get(row["plot"], 0) + int(row["trays"])
named = sorted(plot for plot in totals if plot.startswith("Hill Field"))
if len(named) != 2:
    raise SystemExit("the sheet must carry two plots called Hill Field")
answer = totals["Hill Field (north)"]
other = [totals[plot] for plot in named if plot != "Hill Field (north)"][0]
assert answer != other, "the two plots must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
