# DISTILL-CANARY-e6b1742f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["despatch_log_2026-08.csv"])))
rates = {r["timber_code"]: float(r["cubic_m_per_length"])
         for r in csv.DictReader(io.StringIO(case["files"]["timber_volumes.csv"]))}
volume = sum(int(r["lengths"]) * rates[r["timber_code"]]
             for r in rows if r["customer"] == "Whitcombe Joinery")
print(json.dumps({"expected_number": round(volume, 2)}))
