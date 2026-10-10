# DISTILL-CANARY-c86d1e40 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/guillotine.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE steps=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every step"

stacks = [line for line in lines if re.fullmatch(r"\S+ STACK job=\S+ height=\d+", line)]
print(json.dumps({"expected_number": len(stacks)}))
