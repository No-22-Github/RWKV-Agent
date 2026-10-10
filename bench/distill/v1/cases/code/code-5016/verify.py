# DISTILL-CANARY-6fa8c132 : distillation case
import json
import re

case = json.load(open("case.json"))
match = re.search(r"(?m)^HANDLING_PENCE = (\d+)$", case["files"]["quotes/shipping.py"])
print(json.dumps({"expected_number": int(match.group(1))}))
