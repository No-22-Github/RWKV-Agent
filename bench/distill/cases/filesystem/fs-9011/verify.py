# DISTILL-CANARY-ea8f2e7d : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["releases/CLEANUP.md"].startswith("# Cleanup notes")
n = sum(1 for p in case["files"] if p.startswith("releases/") and p.endswith(".tar.gz"))
print(json.dumps({"expected_number": n}))
