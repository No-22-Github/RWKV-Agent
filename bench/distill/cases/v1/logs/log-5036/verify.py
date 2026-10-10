# DISTILL-CANARY-3ac9f7d1 : distillation case
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
assert {line.split("furnace=")[1].split()[0] for line in runs} == {"F-1", "F-2"}, \
    "the journal does not name both furnaces"
print(json.dumps({"expected_number": sum(
    int(line.split("heats=")[1].split()[0]) for line in runs
    if line.split("furnace=")[1].split()[0] == "F-2")}))
