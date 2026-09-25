# DISTILL-CANARY-4b7c1e93 : distillation case
import json
import re

case = json.load(open("case.json"))
terms = case["files"]["berth-terms.md"]

# Clause 2 is the only clause that sets a notice period.
line = next(l for l in terms.splitlines() if "cancellation must reach the office" in l)
print(json.dumps({"expected_number": int(re.search(r"at least (\d+) days", line).group(1))}))
