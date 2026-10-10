# DISTILL-CANARY-b04c2b59 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/defrost-cycles.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

cycle_re = re.compile(r"^\S+ DEFROST coil=\S+ duration_min=\d+ result=(\S+)$")
summary_re = re.compile(r"^\S+ SUMMARY defrosts_completed=\d+ all_ok=\S+$")
completed = 0
for line in lines[:-1]:
    m = cycle_re.fullmatch(line)
    if m:
        if m.group(1) == "ok":
            completed += 1
    else:
        assert summary_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": completed}))
