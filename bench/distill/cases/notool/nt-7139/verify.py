# DISTILL-CANARY-2c46da7d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["logistics/voyage_log.csv"]))
speed = next(float(r["speed_kn"]) for r in rows
              if r["ship"] == "汐远轮" and r["month"] == "2026-09")
print(json.dumps({"expected_number": speed * 6}))
