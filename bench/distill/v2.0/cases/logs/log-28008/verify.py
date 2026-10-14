# DISTILL-CANARY-af56d73c : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Warehouse export sync worker")
lines = case["files"]["logs/sync-worker.log"].splitlines()
n = next(i + 1 for i, l in enumerate(lines) if "checksum mismatch" in l)
print(json.dumps({"expected_number": n}))
