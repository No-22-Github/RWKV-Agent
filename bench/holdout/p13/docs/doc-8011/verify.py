# DISTILL-CANARY-f6be6e85 : p13 holdout eval case (eval-only, never for training)
import json
import re
import sys

case = json.load(open("case.json"))
text = case["files"]["员工手册-休假制度.md"]
row = None
for line in text.splitlines():
    if line.strip().startswith("| 满 3 年不满 5 年"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        row = cells[-1]
if row is None or not row.isdigit():
    sys.exit(1)
print(json.dumps({"expected_number": int(row)}))
