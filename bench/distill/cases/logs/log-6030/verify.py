# DISTILL-CANARY-b04f36cb : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/funicular-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

arr_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) ARRIVAL car=(\S+) platform=\S+$")
seen = set()
for line in lines[:-1]:
    m = arr_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if m.group(1) == "2026-08-23" and "11:00:00" <= m.group(2) < "12:00:00" and m.group(3) == "B":
        seen.add(m.group(2))
print(json.dumps({"expected_number": len(seen)}))
