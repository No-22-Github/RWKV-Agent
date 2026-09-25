# DISTILL-CANARY-4be4271b : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/scans.log"].splitlines() if line.strip()]
out, delivered = set(), set()
for line in lines:
    match = re.fullmatch(r"\S+ scan=(\w+) parcel=(\S+)", line)
    assert match is not None, "unreadable scan line: " + line
    event, parcel = match.group(1), match.group(2)
    if event == "out":
        out.add(parcel)
    elif event == "delivered":
        delivered.add(parcel)
print(json.dumps({"expected_number": len(out - delivered)}))
