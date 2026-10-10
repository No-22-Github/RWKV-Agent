# DISTILL-CANARY-b04d5f3c : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/weighbridge.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

info_re = re.compile(r"^\S+ weighbridge=\S+ INFO truck=\S+ gross_t=[\d.]+ limit_t=[\d.]+ ok$")
alarm_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):\d{2} weighbridge=\S+ ALARM truck=\S+ gross_t=[\d.]+ limit_t=[\d.]+ oversize$")
first = None
for line in lines[:-1]:
    m = alarm_re.fullmatch(line)
    if m:
        first = (int(m.group(2)), m.group(3))
        break
    assert info_re.fullmatch(line), "unreadable line: " + line
assert first is not None, "no oversize alarm in the journal"
utc_h = first[0] + 3
assert utc_h < 24, "alarm sits at a day boundary in UTC"
print(json.dumps({"expected": f"{utc_h:02d}:{first[1]}"}))
