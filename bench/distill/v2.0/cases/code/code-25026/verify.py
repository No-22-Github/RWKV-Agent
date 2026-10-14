# DISTILL-CANARY-909eb60c : distillation case
import json
import re

case = json.load(open("case.json"))
match = re.search(r"(?m)^HOLD_SECONDS = (\d+)$", case["files"]["press/limits.py"])
print(json.dumps({"expected_number": int(match.group(1))}))
