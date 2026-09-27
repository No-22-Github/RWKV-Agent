# DISTILL-CANARY-b04c087e : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/press-journal.log"].splitlines() if l.strip()]
close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
assert close, "closing record absent"
assert len(lines) - 1 == int(close.group(1)), "line count does not match the closing record"

iso_re = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}) PRESS batch=J-\d+ run_start apples_kg=\d+$")
dmy_re = re.compile(r"^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}) PRESS batch=J-\d+ run_start apples_kg=\d+$")
other_re = re.compile(r"^\S+ .*(run_finish juice_l=\d+|DELIVERY grower=\S+ bins=\d+|QA store_temp_c=[\d.]+ pass|NOTE journal rotated at month end: stamps switch to dd/mm/yyyy)$")
starts = 0
for line in lines[:-1]:
    m = iso_re.fullmatch(line)
    if m:
        if (m.group(2), m.group(3)) in (("03", "31"),):
            starts += 1
        continue
    m = dmy_re.fullmatch(line)
    if m:
        if (m.group(1), m.group(2)) == ("01", "04"):
            starts += 1
        continue
    assert other_re.fullmatch(line), "unreadable line: " + line
print(json.dumps({"expected_number": starts}))
