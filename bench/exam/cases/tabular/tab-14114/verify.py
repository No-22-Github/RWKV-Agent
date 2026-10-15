# EXAM-CANARY-d025202e : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
vals = []
for line in case["files"]["exports/orders.csv"].splitlines()[1:]:
    _id, region, status, total = line.split(",")
    if region == "West" and status == "completed":
        vals.append(float(total))
print(json.dumps({"expected_number": round(sum(vals) / len(vals), 2)}))
