# WORKBANK-CANARY-7c2d9e51 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
text = case["files"]["settings.yaml"]
match = re.search(r"^shutdown_grace_seconds:\s*(\d+)\s*$", text, re.M)
if not match:
    raise SystemExit("shutdown_grace_seconds not set in settings.yaml")
print(json.dumps({"expected_number": int(match.group(1))}))
