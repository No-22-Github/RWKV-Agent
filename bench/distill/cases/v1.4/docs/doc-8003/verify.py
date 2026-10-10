# DISTILL-CANARY-afb8538e : distillation case
import json
import re

case = json.load(open("case.json"))
text = case["files"]["制度/员工手册.md"]
assert text.startswith("# 员工手册")
cap = int(re.search(r"结转上限 (\d+) 天", text).group(1))
print(json.dumps({"expected_number": cap}))
