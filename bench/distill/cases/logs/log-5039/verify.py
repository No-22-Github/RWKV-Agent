# DISTILL-CANARY-c70a94f5 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/bridge-crossings.log"].splitlines() if line.strip()]
rows = [re.fullmatch(r"(\S+) CROSSED at=(\S+) class=\S+ weight=\d+", line)
        for line in lines[:-1]]
assert all(rows), "the journal holds a line that is not a crossing"
close = re.fullmatch(r"\S+ CLOSE records=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(rows) == int(close.group(1)), "the closing line does not cover every record"
assert all(m.group(2)[:19] <= m.group(1)[:19] for m in rows), \
    "a record reached the office before the crossing it describes"

window = [m for m in rows
          if "2026-09-06T06:00:00Z" <= m.group(2) <= "2026-09-06T09:00:00Z"]
print(json.dumps({"expected_number": len(window)}))
