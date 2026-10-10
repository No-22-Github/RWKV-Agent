# DISTILL-CANARY-95b4e08c : distillation case
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


def tonnes(line, field):
    return int(line.split(field + "=")[1].split()[0])


assert all(tonnes(line, "charged") > tonnes(line, "tapped") for line in runs), \
    "a run does not show a melt loss between charged and tapped"
print(json.dumps({"expected_number": sum(tonnes(line, "tapped") for line in runs)}))
