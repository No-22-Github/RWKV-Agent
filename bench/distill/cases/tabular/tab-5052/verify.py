# DISTILL-CANARY-8f5a4224 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["cask_fills_2026_q2.csv"])))
sizes = {r["fill_id"]: int(r["cask_size_litres"]) for r in rows}
casks = sum(2 if s > 300 else 1 for s in sizes.values())
print(json.dumps({"expected_number": round(2.40 * casks, 2)}))
