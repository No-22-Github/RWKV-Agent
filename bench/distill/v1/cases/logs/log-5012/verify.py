# DISTILL-CANARY-28c48517 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/yard.log"].splitlines() if line.strip()]
trailer = re.fullmatch(r"\S+ CLOSE movements=(\d+)", lines[-1])
assert trailer is not None, "closing record missing"
rows = [re.fullmatch(r"(\S+) (OUT|IN) +vehicle=(\S+)", line) for line in lines[:-1]]
assert all(rows), "unreadable movement line"
assert len(rows) == int(trailer.group(1)), "the journal does not list every movement"

# The controller stamps movements on the depot clock, which runs eight hours
# ahead of UTC, so 06:00-07:00 UTC on 21 August is 14:00-15:00 on that clock.
left = 0
for row in rows:
    stamp, kind = row.group(1), row.group(2)
    if kind == "OUT" and "14:00:00" <= stamp.split("T")[1] < "15:00:00":
        left += 1
print(json.dumps({"expected_number": left}))
