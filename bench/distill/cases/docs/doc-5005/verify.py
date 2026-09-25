# DISTILL-CANARY-c81b4f27 : distillation case
import json
import re

case = json.load(open("case.json"))
guide = case["files"]["artwork-guide.md"]

line = next(l for l in guide.splitlines() if "dots per inch" in l)
print(json.dumps({"expected_number": int(re.search(r"no less than (\d+) dots per inch", line).group(1))}))
