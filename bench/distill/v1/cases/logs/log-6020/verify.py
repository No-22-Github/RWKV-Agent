# DISTILL-CANARY-b04b0f8e : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/reconciliation.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

check_re = re.compile(r"^\S+ booking=(\S+) card_check (ok|cvv_mismatch)$")
summary_re = re.compile(r"^\S+ SUMMARY bookings_checked=\d+ exceptions=\d+ reconciliation \S+$")
failed = []
for line in lines[:-1]:
    m = check_re.fullmatch(line)
    if m:
        if m.group(2) == "cvv_mismatch":
            failed.append(m.group(1))
    else:
        assert summary_re.fullmatch(line), "unreadable line: " + line
assert len(failed) == 1, "the evidence should show exactly one failed check"
print(json.dumps({"expected": failed[0]}))
