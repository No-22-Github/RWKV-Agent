# DISTILL-CANARY-da9531c6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kiln/firings-2026-09.csv"])))
cone6 = [r for r in rows if r["cone"] == "6"]
g207 = [r for r in cone6 if r["glaze"] == "G-207"]
out = {
    "expected_number": len(rows),
    "expected_turn_2": len(cone6),
    "expected_turn_4": len(g207),
    "expected_turn_5": round(sum(float(r["hours"]) for r in g207) / len(g207), 2),
}
print(json.dumps(out))
