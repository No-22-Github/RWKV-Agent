# DISTILL-CANARY-dd01ed72 : distillation case
import csv
import datetime
import io
import json
import re

case = json.load(open("case.json"))
months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
def parse(s):
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m:
        return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.match(r"^([A-Za-z]{3}) (\d{1,2}), (\d{4})$", s)
    if m:
        return datetime.date(int(m.group(3)), months[m.group(1)], int(m.group(2)))
    raise ValueError(s)
rows = list(csv.DictReader(io.StringIO(case["files"]["bookings/july-2026.csv"])))
starts = [parse(r["start_date"]) for r in rows]
t1 = sum(1 for d in starts if datetime.date(2026, 7, 6) <= d <= datetime.date(2026, 7, 12))
t2 = sum(1 for d in starts if datetime.date(2026, 7, 20) <= d <= datetime.date(2026, 7, 26))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
