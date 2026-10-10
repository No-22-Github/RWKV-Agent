# DISTILL-CANARY-4f2b9a71 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/lift-controller.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE events=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every event"

fault = re.compile(r"\S+ FAULT floor=(\d+) code=\S+ door=\d+")
floors = [m.group(1) for m in (fault.fullmatch(line) for line in lines) if m]
assert len(floors) == 1, "the journal does not hold exactly one fault line"
print(json.dumps({"expected_number": int(floors[0])}))
