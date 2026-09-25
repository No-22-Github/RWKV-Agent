# DISTILL-CANARY-f7133cd3 : distillation case
import json

MARKER = "LEDGER-PINNED"
PACKAGE = "payments/"

case = json.load(open("case.json"))

count = 0
for path, content in case["files"].items():
    if not path.startswith(PACKAGE):
        continue
    count += sum(1 for line in content.splitlines() if MARKER in line)

print(json.dumps({"expected_number": count}))
