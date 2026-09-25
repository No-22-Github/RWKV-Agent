# DISTILL-CANARY-7c2f4a9e : distillation case
import json
import re

case = json.load(open("case.json"))
terms = case["files"]["competition-terms.md"]

# Clause 2 is the only clause that sets a withdrawal period.
line = next(l for l in terms.splitlines() if "withdraws from a match gets the entry fee back" in l)
print(json.dumps({"expected_number": int(re.search(r"at least (\d+) days", line).group(1))}))
