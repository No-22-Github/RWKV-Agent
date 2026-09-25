# DISTILL-CANARY-85896f53 : distillation case
import json
import re

case = json.load(open("case.json"))
terms = case["files"]["terms/terms-of-sale.md"]
confirmation = case["files"]["orders/SC-2291-thistlebank.md"]

# A line shown against a build number falls under the made-to-specification
# clause; without one the catalogue stock clause would govern instead.
marker = "build number" if re.search(r"BN-\d{3,}", confirmation) else "catalogue"
line = next(l for l in terms.splitlines() if marker in l and "days of delivery" in l)
days = int(re.search(r"(\d+) days of delivery", line).group(1))
print(json.dumps({"expected_number": days}))
