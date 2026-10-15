# EXAM-CANARY-57bc9619 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import datetime as dt
closed = {dt.date.fromisoformat(l.split()[0]) for l in case["files"]["calendar/closures.txt"].splitlines() if l[:2] == "20"}
d = dt.date(2026, 9, 16); n = 0
while n < 15:
    d += dt.timedelta(days=1)
    if d.weekday() < 5 and d not in closed:
        n += 1
print(json.dumps({"expected_contains_any": [d.isoformat(), d.strftime("%B ") + str(d.day), d.strftime("%b ") + str(d.day), "%d %s" % (d.day, d.strftime("%B")), "%d %s" % (d.day, d.strftime("%b")), "%d/%d/%d" % (d.month, d.day, d.year), "%d月%d日" % (d.month, d.day)]}))
