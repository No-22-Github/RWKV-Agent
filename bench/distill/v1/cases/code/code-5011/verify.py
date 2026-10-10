# DISTILL-CANARY-74ea3d19 : distillation case
import json

MARKER = "WAIVER-OPEN"
case = json.load(open("case.json"))

count = 0
for path, text in case["files"].items():
    if not path.startswith("waivers/"):
        continue
    for line in text.splitlines():
        comment = line.split("#", 1)[1] if "#" in line else ""
        if MARKER in comment:
            count += 1
print(json.dumps({"expected_number": count}))
