# DISTILL-CANARY-3f8b6e14 : distillation case
import json
import re

case = json.load(open("case.json"))
terms = case["files"]["supply-terms.md"]

# The delivery clause is the only one that puts a deadline on reporting damage.
line = next(l for l in terms.splitlines() if "Damage found once the pallet is open" in l)
print(json.dumps({"expected_number": int(re.search(r"within (\d+) days of delivery", line).group(1))}))
