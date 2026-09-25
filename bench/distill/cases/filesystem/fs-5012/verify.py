# DISTILL-CANARY-8e623e29 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

sheet = case["files"]["curve-sheet-narrow-gauge.txt"]
match = re.search(r"^Smallest radius used:\s*([0-9.]+)\s*mm", sheet, re.M)
answer = float(match.group(1)) if match else "UNKNOWN"
print(json.dumps({"expected_number": answer}))
