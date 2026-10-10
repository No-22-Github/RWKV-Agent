# DISTILL-CANARY-b9a2669c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
log = list(csv.DictReader(io.StringIO(case["files"]["forecourt/fuel_log_2026-08.csv"])))
settle = list(csv.DictReader(io.StringIO(case["files"]["forecourt/card_settlements_2026-08.csv"])))
short = sum(float(r["amount"]) for r in log) - sum(float(r["amount"]) for r in settle)
print(json.dumps({"expected_number": round(short, 2)}))
