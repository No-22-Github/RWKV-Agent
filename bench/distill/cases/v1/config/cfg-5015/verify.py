# DISTILL-CANARY-1f6d3b92 : distillation case
import json

case = json.load(open("case.json"))

# README.md: the line's sheet is the two sheets folded together, and a setting
# appears in one of them only.
count = 0
for path, text in case["files"].items():
    if not path.endswith(".yaml"):
        continue
    count += sum(1 for line in text.splitlines() if line.strip() and ":" in line)

print(json.dumps({"expected_number": count}))
