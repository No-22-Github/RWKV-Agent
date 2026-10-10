# DISTILL-CANARY-9d27e5b0 : distillation case
import json
import re

case = json.load(open("case.json"))
match = re.search(r"(?m)^STUCK_POLLS = (\d+)$", case["files"]["press/limits.py"])
print(json.dumps({"expected_number": int(match.group(1))}))
