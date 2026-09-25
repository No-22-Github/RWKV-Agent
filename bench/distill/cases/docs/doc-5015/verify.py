# DISTILL-CANARY-a57d0e28 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

# Every path named by the list is checked against the folder itself.
named = [line.strip() for line in files["lists/event-set.txt"].splitlines() if line.strip()]
missing = {path for path in named if path not in files}

print(json.dumps({"expected_number": len(missing)}))
