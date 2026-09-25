# DISTILL-CANARY-7d3e5a91 : distillation case
import json
import re

case = json.load(open("case.json"))
style = case["files"]["house-style.md"]

# The applicability window is stated on the sheet itself.
line = next(l for l in style.splitlines() if "applies to manuscripts submitted between" in l)
print(json.dumps({"expected_number": int(re.search(r"Edition (\d+)", line).group(1))}))
