# DISTILL-CANARY-9a3f60dc : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/genset.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE events=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the log does not list every event"

runs = []
for index, line in enumerate(lines):
    if re.fullmatch(r"2026-09-05\S+ START genset=\S+", line) is None:
        continue
    for later in lines[index + 1:]:
        stop = re.fullmatch(r"\S+ STOP genset=\S+ run_seconds=(\d+)", later)
        if stop is not None:
            runs.append(int(stop.group(1)))
            break
assert len(runs) == 1, "the log does not hold exactly one run that began on 5 September"
print(json.dumps({"expected_number": runs[0]}))
