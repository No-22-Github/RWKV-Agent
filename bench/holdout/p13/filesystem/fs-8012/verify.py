# DISTILL-CANARY-c60308d9 : p13 holdout eval case (eval-only, never for training)
import json
import sys

case = json.load(open("case.json"))
count = 0
for path, content in case["files"].items():
    if not path.endswith(".sql"):
        continue
    lines = content.splitlines()
    if not lines or not lines[0].strip().startswith("-- type: full"):
        continue
    count += 1
if count == 0:
    sys.exit(1)
print(json.dumps({"expected_number": count}))
