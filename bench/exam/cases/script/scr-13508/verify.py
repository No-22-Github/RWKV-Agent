# EXAM-CANARY-4b19d7a0 : exam gap-fill case
import json,csv,io
case=json.load(open("case.json",encoding="utf-8"))
t=0.0
for r in csv.DictReader(io.StringIO(case["files"]["data/orders.csv"])):
    if r["status"]!="cancelled": t+=float(r["gross"])-float(r["refund"])
print(json.dumps({"expected_number":round(t,2)}))
