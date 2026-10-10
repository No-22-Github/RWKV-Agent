# DISTILL-CANARY-08d3a6e1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["deliveries-2026-09.csv"])))
kitchen = [r for r in rows if r["supplier"] != "Fernhall market run"]
out = {
    "expected_number": sum(int(r["bags"]) for r in rows),
    "expected_turn_2": sum(int(r["bags"]) for r in kitchen),
}
print(json.dumps(out))
