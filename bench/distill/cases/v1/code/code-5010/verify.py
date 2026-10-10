# DISTILL-CANARY-f20b7c48 : distillation case
import json

MARKER = "CHECKUP-PINNED"
case = json.load(open("case.json"))

count = 0
for path, text in case["files"].items():
    if not path.startswith("tools/"):
        continue
    count += sum(1 for line in text.splitlines() if MARKER in line)
print(json.dumps({"expected_number": count}))
