# DISTILL-CANARY-e2816b04 : distillation case
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"]
log = case["files"]["logs/melting-shift.log"]
assert readme.startswith("# Thorneybank Foundry - melting shift journal\n"), \
    "README.md does not document the journal"
lines = [line for line in log.splitlines() if line.strip()]
run_re = re.compile(r"\S+ RUN batch=\d+ furnace=F-\d heats=\d+ charged=\d+ tapped=\d+")
runs = [line for line in lines if run_re.fullmatch(line)]
summary = re.fullmatch(r"\S+ SHIFT runs=(\d+) heats=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(runs) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every run"
assert sum(int(line.split("heats=")[1].split()[0]) for line in runs) == int(summary.group(2)), \
    "the summary heat count disagrees with the runs"

# A run line carries the batch, the furnace, the heats it fired and the tonnes
# charged and tapped, and the closing line counts runs and heats. No grade is
# written down anywhere in the workspace, so the heats melted for one grade
# cannot be counted.
for line in lines[:-1]:
    assert run_re.fullmatch(line), "unexpected journal line: " + line
assert "grade" not in (readme + log).lower(), "a grade record appeared in the workspace"
print(json.dumps({"expected_contains_any": ["grade", "grades", "D2"]}))
