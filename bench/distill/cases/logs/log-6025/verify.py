# DISTILL-CANARY-b04a68de : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/spray-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

spray_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) SPRAY block=\S+ rows=\d+ litres=\d+ nozzle=\S+$")
count = 0
for line in lines[:-1]:
    m = spray_re.fullmatch(line)
    assert m, "unreadable line: " + line
    if m.group(1) == "2026-08-12" and "05:00:00" <= m.group(2) < "07:00:00":
        count += 1
print(json.dumps({"expected_number": count}))
