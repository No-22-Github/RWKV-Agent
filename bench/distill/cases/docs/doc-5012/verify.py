# DISTILL-CANARY-d31b8e57 : distillation case
import json
import re

case = json.load(open("case.json"))
terms = case["files"]["conditions/hire-terms.md"]

# The conditions set a load limit for each kind of skip.
line = next(l for l in terms.splitlines() if "household skip may carry" in l)
print(json.dumps({"expected_number": int(re.search(r"up to (\d+) tonnes", line).group(1))}))
