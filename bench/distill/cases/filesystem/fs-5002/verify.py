# DISTILL-CANARY-cbfe778f : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

card = ""
for path in sorted(case["files"]):
    content = case["files"][path]
    if "navy buckram" in content:
        card = content
        break

match = re.search(r"Board:\s*([0-9.]+)\s*mm", card)
print(json.dumps({"expected_number": float(match.group(1))}))
