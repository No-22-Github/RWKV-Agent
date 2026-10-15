# EXAM-CANARY-c40b6e73 : exam gap-fill case
import json,csv,io
case=json.load(open("case.json",encoding="utf-8"))
r=csv.DictReader(io.StringIO(case["files"]["data/sales_2026.csv"]))
print(json.dumps({"expected_number":round(sum(float(x["amount"]) for x in r),2)}))
