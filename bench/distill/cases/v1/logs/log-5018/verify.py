# DISTILL-CANARY-e15c74b2 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/silo.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE draws=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the log does not list every draw"

draws = [line for line in lines
         if re.fullmatch(r"2026-09-22\S+ DRAW silo=S-2 batch=\S+ kg=\d+", line)]
print(json.dumps({"expected_number": len(draws)}))
