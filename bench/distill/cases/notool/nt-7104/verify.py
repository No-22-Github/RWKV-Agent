# DISTILL-CANARY-d41a6f02 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["assets/storage_plan.csv"]))
caps_gb = [float(r["capacity_gb"]) for r in rows]
# RAID1 mirrors the data: usable space equals the smallest single disk.
print(json.dumps({"expected_number": min(caps_gb) / 1024}))
