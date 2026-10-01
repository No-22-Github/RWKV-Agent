# DISTILL-CANARY-8048a035 : p13 holdout eval case (eval-only, never for training)
import json
import os
import sys

case = json.load(open("case.json"))
files = case["files"]
HEADER = "对账日期,流水号,收支方向,金额(元),余额"
for path, content in files.items():
    if path.endswith(".csv"):
        first = content.splitlines()[0].strip() if content.splitlines() else ""
        if first != HEADER:
            sys.exit(1)
candidates = [
    path for path in files
    if path.endswith(".csv") and "2025Q4" in path and "final" in path and "draft" not in path
]
if len(candidates) != 1:
    sys.exit(1)
print(json.dumps({"expected_string": os.path.basename(candidates[0])}))
