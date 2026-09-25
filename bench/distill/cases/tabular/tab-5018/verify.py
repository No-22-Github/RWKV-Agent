# DISTILL-CANARY-8ea507b4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press_log_2026.csv"])))
june = sum(int(r["litres_pressed"]) for r in rows if r["press_month"] == "2026-06")
july = sum(int(r["litres_pressed"]) for r in rows if r["press_month"] == "2026-07")
print(json.dumps({"expected_number": round((july - june) / june * 100, 1)}))
