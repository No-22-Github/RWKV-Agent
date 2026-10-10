# DISTILL-CANARY-1f6deb23 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/storm-pump.log"].splitlines() if line.strip()]
runs = [line for line in lines
        if re.fullmatch(r"\S+ RUN pump=\S+ minutes=\d+ level=\d+", line)]
close = re.fullmatch(r"\S+ CLOSE runs=(\d+) storm=(\d+) duty=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(runs) == len(lines) - 1 == int(close.group(1)), \
    "the closing line does not cover every run"
assert sum(1 for line in runs if "pump=storm" in line) == int(close.group(2)), \
    "the closing storm count disagrees with the journal"
assert {line.split("pump=")[1].split()[0] for line in runs} == {"duty", "storm"}, \
    "the journal does not name both pumps"

window = [line for line in runs if "pump=storm" in line
          and "2026-09-06T01:00:00Z" <= line.split()[0] <= "2026-09-06T06:00:00Z"]
print(json.dumps({"expected_number": len(window)}))
