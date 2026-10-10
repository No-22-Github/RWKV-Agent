# DISTILL-CANARY-1e9d30b6 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/boiler.log"].splitlines() if line.strip()]
rows = []
for line in lines:
    m = re.fullmatch(r"\S+ CYCLE burner=\S+ load=(\d+) minutes=\d+ fuel=(\d+)", line)
    if m:
        rows.append((int(m.group(1)), int(m.group(2))))
summary = re.fullmatch(r"\S+ SUMMARY session=\S+ cycles=(\d+) fuel=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(rows) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every cycle line"
print(json.dumps({"expected_number": sum(load for load, fuel in rows if fuel > 70)}))
