# DISTILL-CANARY-1509cb6d : distillation case
import json

MARKER = "REPLAY-HOLD"
PACKAGE = "replay/"
case = json.load(open("case.json"))

count = 0
for path, text in case["files"].items():
    if not path.startswith(PACKAGE):
        continue
    for line in text.splitlines():
        comment = line.split("#", 1)[1] if "#" in line else ""
        if MARKER in comment:
            count += 1
print(json.dumps({"expected_number": count}))
