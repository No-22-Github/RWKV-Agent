# DISTILL-CANARY-d68ff654 : distillation case
import json
import re

with open("case.json") as handle:
    case = json.load(handle)

answer = "UNKNOWN"
for path in sorted(case["files"]):
    if not path.startswith("batches/"):
        continue
    match = re.search(r"^Drum (\d+) - amber malt", case["files"][path], re.M)
    if match:
        answer = match.group(1)
        break

print(json.dumps({"expected_string": answer}))
