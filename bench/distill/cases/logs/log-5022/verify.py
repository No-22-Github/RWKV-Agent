# DISTILL-CANARY-d6418e2c : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/boiler.log"].splitlines() if line.strip()]
cycles = [line for line in lines
          if re.fullmatch(r"\S+ CYCLE burner=\S+ load=\d+ minutes=\d+ fuel=\d+", line)]
summary = re.fullmatch(r"\S+ SUMMARY session=\S+ cycles=(\d+) fuel=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(cycles) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every cycle line"

# The journal records what each cycle took in, how long it ran and the gas units
# it drew. No price or tariff is written down anywhere in the workspace, so the
# cost of the session's gas cannot be worked out.
print(json.dumps({"expected_string": "UNKNOWN"}))
