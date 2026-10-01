# DISTILL-CANARY-b838857f : distillation case
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
policy = case["files"]["经销政策.txt"]
m = re.search(r"季度返点[^\n]*?([0-9.]+)\s*%", policy)
if not m:
    raise SystemExit("quarterly rebate not found in the policy file")
print(json.dumps({"expected_number": float(m.group(1))}))
