# DISTILL-CANARY-c80fed93 : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Payments service.")
assert case["files"]["db/migrations/README.md"].startswith("Apply in numeric order")
n = sum(1 for p in case["files"] if p.startswith("db/migrations/") and p.endswith(".sql"))
print(json.dumps({"expected_number": n}))
