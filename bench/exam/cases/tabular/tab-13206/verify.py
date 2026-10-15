# EXAM-CANARY-833eb3c3 : exam gap-fill case
import csv, io, json
case = json.load(open("case.json", encoding="utf-8"))
tot = 0
for r in csv.DictReader(io.StringIO(case["files"]["sales.csv"])):
    if r["store"] == "Austin" and r["month"] == "2026-08":
        tot += int(r["units"])
print(json.dumps({"expected": tot}))
