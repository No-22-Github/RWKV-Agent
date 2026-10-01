# DISTILL-CANARY-a250327d : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/db-slowquery.log"].splitlines()

all_slow = []
morning = []
morning_no_etl = []
best = 0.0
for line in lines:
    m = re.search(r"^(\S+ \S+) dur=([\d.]+)s", line)
    if not m:
        continue
    ts = m.group(1)
    dur = float(m.group(2))
    user = re.search(r"user=(\S+)", line).group(1)
    if dur > 5.0:
        row = (ts, dur, user)
        all_slow.append(row)
        if "2026-09-22 00:00:00" <= ts < "2026-09-22 03:00:00":
            morning.append(row)
            if user != "etl_batch":
                morning_no_etl.append(row)
                best = max(best, dur)

forms = [
    "%d 条" % len(all_slow),
    "%d 条" % len(morning),
    "%d 条" % len(morning_no_etl),
    "%s" % best,
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
