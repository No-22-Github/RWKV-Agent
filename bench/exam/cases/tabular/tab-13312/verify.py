# EXAM-CANARY-f17c4a3d : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.reader(io.StringIO(case["files"]["deliveries.csv"])))
assert rows[0] == ["date", "courier", "route", "km", "status"]
print(json.dumps({"expected": round(sum(float(r[3]) for r in rows[1:] if r[1] == "C-17" and r[0][:7] == "2026-09" and r[4] == "completed"), 1)}))
