# DISTILL-CANARY-b04e36fb : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/feeder.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

feed_re = re.compile(r"^\S+ pen=(\S+) feed_kg=[\d.]+ drop$")
note_re = re.compile(r"^\S+ NOTE .+$")
drops = 0
for line in lines[:-1]:
    m = feed_re.fullmatch(line)
    if m:
        if m.group(1) == "K-3":
            drops += 1
    else:
        assert note_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": drops}))
