# DISTILL-CANARY-34e27ca8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["output/line_output_2026-05.csv"])))
vals = []
for r in rows:
    if r["line"] != "Line 2":
        continue
    try:
        vals.append(float(r["units_output"]))
    except ValueError:
        pass
print(json.dumps({"expected_number": round(sum(vals) / len(vals), 2)}))
