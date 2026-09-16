"""Expected answer for log-0003: label rejections on Sep 1-2, 2026 (dash stamps are day-first)."""
import json
import re
from datetime import date

case = json.load(open("case.json"))
log = case["files"]["logs/carrier-webhook.log"]
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
lo, hi = date(2026, 9, 1), date(2026, 9, 2)
count = 0
for line in log.splitlines():
    if "E_LABEL_REJECT" not in line:
        continue
    m = re.match(r"(\d{4})/(\d{2})/(\d{2}) ", line)
    if m:
        day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    else:
        m = re.match(r"(\d{2})-(\d{2})-(\d{4}) ", line)
        if m:
            # dash stamps are day-first per the README convention
            day = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        else:
            m = re.match(r"([A-Za-z]{3}) (\d{1,2}), (\d{4}) ", line)
            if not m:
                raise SystemExit("unrecognized timestamp style: %s" % line)
            day = date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    if lo <= day <= hi:
        count += 1
print(json.dumps({"expected_number": count}))
