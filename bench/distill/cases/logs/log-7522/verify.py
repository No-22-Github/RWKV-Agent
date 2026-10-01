# DISTILL-CANARY-98f1f45d : distillation case
import json
import re
from datetime import datetime, timedelta

case = json.load(open("case.json"))
sheet = case["files"]["notes/thresholds.md"]
log = case["files"]["logs/db-slowquery.log"].splitlines()

classes = []
for m in re.finditer(r"\(([^)]+)\): dur > ([\d.]+) s", sheet):
    for db in m.group(1).split(","):
        classes.append((db.strip(), float(m.group(2))))
limit_for = dict(classes)

slow = []
for line in log:
    m = re.search(r"^(\S+ \S+) dur=([\d.]+)s db=(\S+)", line)
    if not m:
        continue
    ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
    db = m.group(3)
    lim = limit_for.get(db)
    if lim is not None and float(m.group(2)) > lim:
        slow.append((ts, db, float(m.group(2))))

# turn 1: a reporting-class db with more than 5 slow rows in any 10-minute window
by_db = {}
for ts, db, _ in slow:
    by_db.setdefault(db, []).append(ts)
alert_db = ""
for db, tss in sorted(by_db.items()):
    if limit_for[db] == 3.0:
        tss.sort()
        for i in range(len(tss)):
            win = [t for t in tss if tss[i] <= t < tss[i] + timedelta(minutes=10)]
            if len(win) > 5:
                alert_db = db
                break
    if alert_db:
        break

total = len(slow)
longest = "%.1f" % max(d for _, _, d in slow)
no_analytics = sum(1 for _, db, _ in slow if db != "analytics")

forms = [alert_db, "%d slow" % total, "%d queries" % total, longest,
         "%d slow" % no_analytics, "%d queries" % no_analytics]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
