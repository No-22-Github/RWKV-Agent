# DISTILL-CANARY-5f7f2a5a : distillation case
import json
import re

case = json.load(open("case.json"))
match = re.search(r"(?m)^MIN_CHARGE_PENCE = (\d+)$", case["files"]["orders/quote.py"])
print(json.dumps({"expected_number": int(match.group(1))}))
