# DISTILL-CANARY-d475d96f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/订单流水.csv"]))
total = 0.0
for r in rows:
    if r["套系"] == "写真" and float(r["实收"]) > 3000:
        total += float(r["实收"])
print(json.dumps({"expected_number": round(total, 2)}))
