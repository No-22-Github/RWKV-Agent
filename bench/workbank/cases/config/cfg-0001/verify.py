# WORKBANK-CANARY-9f34c1ab : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
text = case["files"]["services/notify-hub.yaml"]
match = re.search(r"^port:\s*(\d+)\s*$", text, re.M)
if not match:
    raise SystemExit("no port key in notify-hub.yaml")
print(json.dumps({"expected_number": int(match.group(1))}))
