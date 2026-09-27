# DISTILL-CANARY-b04e8b25 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/weighbridge.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

out_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) WEIGH-OUT trailer=\S+ gross=(\d+) tare=(\d+)$")
arrive_re = re.compile(r"^\S+ ARRIVE trailer=\S+$")
net = 0
for line in lines[:-1]:
    m = out_re.fullmatch(line)
    if m:
        if m.group(1) == "2026-05-07" and "13:00:00" <= m.group(2) < "14:00:00":
            net += int(m.group(3)) - int(m.group(4))
    else:
        assert arrive_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": net}))
