# DISTILL-CANARY-16529d05 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["销售/9月门店流水.csv"])))
total = round(sum(float(r["金额"]) for r in rows if r["门店"] == "静安店"), 2)
print(json.dumps({"expected_number": round(total / 10000, 2)}))
