# DISTILL-CANARY-63f78fe7 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["差旅报销-2026-09.csv"]))
travel = 0.0
writeoff = 0.0
for r in rows:
    kind = r["类型"].strip()
    if kind == "出差报销":
        travel += float(r["金额(元)"])
    elif kind == "冲销":
        writeoff += float(r["金额(元)"])
print(json.dumps({"expected_number": round(travel - writeoff, 2)}))
