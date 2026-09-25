# DISTILL-CANARY-1ff7f8d9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
intake = list(csv.DictReader(io.StringIO(case["files"]["kiln_intake_2026-08.csv"])))
packing = list(csv.DictReader(io.StringIO(case["files"]["packing_records_2026-08.csv"])))
kg_in = {r["intake_id"]: float(r["kg_in"]) for r in intake}
kg_out = sum(float(r["kg_out"]) for r in packing)
print(json.dumps({"expected_number": round(sum(kg_in.values()) - kg_out, 1)}))
