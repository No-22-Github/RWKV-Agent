# DISTILL-CANARY-971a49d0 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
roster = {}
for r in csv.DictReader(io.StringIO(case["files"]["商户表.csv"])):
    roster[r["商户名称"].strip()] = r["商户编号"].strip()
code = roster["南风书屋"]
total = 0.0
for line in case["files"]["payments-202609.jsonl"].splitlines():
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    if rec.get("merchant") == code and rec.get("status") == "success":
        total += float(rec["amount"])
print(json.dumps({"expected_number": round(total, 2)}))
