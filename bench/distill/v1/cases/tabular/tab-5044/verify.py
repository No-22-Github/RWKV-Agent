# DISTILL-CANARY-70f89953 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["lorry_loads_2026-08.csv"])))
loads = {r["load_id"] for r in rows if r["haulier"] == "Coldborough Transport"}
print(json.dumps({"expected_number": len(loads)}))
