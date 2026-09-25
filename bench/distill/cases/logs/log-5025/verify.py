# DISTILL-CANARY-a4c623d8 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/intake.log"].splitlines() if line.strip()]
close = re.fullmatch(r"\S+ CLOSE tankers=(\d+)", lines[-1])
assert close is not None, "closing line missing"
assert len(lines) - 1 == int(close.group(1)), "the journal does not list every tanker"

rows = []
for line in lines[:-1]:
    m = re.fullmatch(r"2026-09-16T(\d\d):(\d\d):(\d\d)Z TANKER farm=\S+ litres=(\d+)", line)
    assert m is not None, "unreadable tanker line: " + line
    # the intake bay stamps the plant clock, which runs three hours ahead of UTC
    hour = (int(m.group(1)) - 3) % 24
    rows.append((hour, int(m.group(4))))

total = sum(litres for hour, litres in rows if 3 <= hour < 6)
print(json.dumps({"expected_number": total}))
