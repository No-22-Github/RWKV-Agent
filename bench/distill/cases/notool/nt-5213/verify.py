# DISTILL-CANARY-5b16da4f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["patrols/rate-card-2026-09.csv"]))
rate = next(r["nightly_gbp"] for r in rows if r["visits_per_night"] == "4")
print(json.dumps({"expected_number": float(rate)}))
