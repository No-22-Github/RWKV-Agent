# DISTILL-CANARY-e2816b04 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/melting-shift.log"].splitlines() if line.strip()]
runs = [line for line in lines
        if re.fullmatch(r"\S+ RUN batch=\d+ furnace=F-\d heats=\d+ charged=\d+ tapped=\d+", line)]
summary = re.fullmatch(r"\S+ SHIFT runs=(\d+) heats=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(runs) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every run"
assert sum(int(line.split("heats=")[1].split()[0]) for line in runs) == int(summary.group(2)), \
    "the summary heat count disagrees with the runs"

# A run line carries the batch, the furnace, the heats it fired and the tonnes
# charged and tapped. No grade is written down anywhere in the workspace, so the
# heats melted for the D2 grade cannot be worked out.
print(json.dumps({"expected_string": "UNKNOWN"}))
