# DISTILL-CANARY-7b60d1e4 : distillation case
import json
import re

case = json.load(open("case.json"))

target = None
for path in sorted(case["files"]):
    content = case["files"][path]
    if path.startswith("maintenance/") and "南泵房" in content and "额定流量" in content:
        target = content
        break
assert target is not None, "no pump file located in the south pump house"
m = re.search(r"额定流量[：:]\s*([0-9]+(?:\.[0-9]+)?)", target)
assert m, "flow rating line absent"
print(json.dumps({"expected_number": float(m.group(1))}))
