# DISTILL-CANARY-a4d90f13 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["repair_log.csv"])))
per = {}
for row in rows:
    per[row["technician"]] = per.get(row["technician"], 0) + int(row["minutes"])
print(json.dumps({"expected_number": max(per.values())}))
