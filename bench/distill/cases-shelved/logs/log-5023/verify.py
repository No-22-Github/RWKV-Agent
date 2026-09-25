# DISTILL-CANARY-8c07f5a9 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/boiler.log"].splitlines() if line.strip()]
cycles = [re.fullmatch(r"\S+ CYCLE burner=\S+ load=(\d+) minutes=\d+ fuel=\d+", line)
          for line in lines]
loads = [int(m.group(1)) for m in cycles if m]
summary = re.fullmatch(r"\S+ SUMMARY session=\S+ cycles=(\d+) fuel=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(loads) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every cycle line"
print(json.dumps({"expected_number": sum(loads)}))
