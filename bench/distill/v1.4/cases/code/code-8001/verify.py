# DISTILL-CANARY-d046a15f : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Billing service.")
defs = [(p, m) for p, t in files.items() if p.endswith(".py") for m in re.findall(r"^def (\w+)\(", t, re.M) if "invoice" in m and "round" in m]
assert len(defs) == 1
print(json.dumps({"expected_string": defs[0][0]}))
