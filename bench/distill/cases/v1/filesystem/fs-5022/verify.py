# DISTILL-CANARY-715c7c59 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

sheet = case["files"]["batch-sheets/ash-2418.txt"]
match = re.search(r"^Finished diameter:\s*([0-9.]+)\s*mm", sheet, re.M)
diameter = float(match.group(1)) if match else "UNKNOWN"
print(json.dumps({"expected_number": diameter}))
