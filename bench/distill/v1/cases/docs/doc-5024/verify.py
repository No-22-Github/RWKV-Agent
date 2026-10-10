# DISTILL-CANARY-9a4d7c26 : distillation case
import json
import re

case = json.load(open("case.json"))
register = case["files"]["plan-register.md"]

# The register states the window each revision covers, so the revision that
# governs the winter working is the one whose window carries the date.
line = next(l for l in register.splitlines() if "applies to working between" in l)
print(json.dumps({"expected_number": int(re.search(r"Revision (\d+)", line).group(1))}))
