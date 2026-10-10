# DISTILL-CANARY-b04d2e90 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/cip-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

start_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) CIP circuit=\S+ start$")
other_re = re.compile(r"^\S+ CIP circuit=\S+ complete duration_min=\d+$")
rinse_re = re.compile(r"^\S+ RINSE circuit=\S+ drained$")
check_re = re.compile(r"^\S+ CHECK circuit=\S+ conductivity_uS=[\d.]+ pass$")
count = 0
for line in lines[:-1]:
    m = start_re.fullmatch(line)
    if m:
        if m.group(1) == "2026-02-19" and "02:00:00" <= m.group(2) < "04:00:00":
            count += 1
    else:
        assert other_re.fullmatch(line) or rinse_re.fullmatch(line) or check_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": count}))
