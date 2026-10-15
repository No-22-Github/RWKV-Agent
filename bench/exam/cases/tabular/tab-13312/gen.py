#!/usr/bin/env python3
"""Generates tab-13312 (en, total km for one courier in September, completed runs only, 2,600-row CSV)."""
import csv, datetime, io, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX, prefix_lines

CANARY = "EXAM-CANARY-f17c4a3d"
rng = random.Random(13312)
COUR = ["C-%02d" % n for n in (3, 8, 11, 17, 21, 26, 34)]
ROUTES = ["Dockside loop", "Airport freight", "Central market", "Hillcrest run", "Ring road night", "Harbor parcels"]
N = 2600
start = datetime.date(2026, 6, 1)
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 108 / N))
    st = rng.choices(["completed", "cancelled", "partial"], [86, 9, 5])[0]
    rows.append([d.isoformat(), rng.choice(COUR), rng.choice(ROUTES), "%.1f" % rng.uniform(2, 64), st])
buf = io.StringIO(newline="")
w = csv.writer(buf, lineterminator="\n")
w.writerow(["date", "courier", "route", "km", "status"])
w.writerows(rows)
text = buf.getvalue()
size = check_size(text, 80_000, 200_000)


def tot(rs, month="2026-09", sts=("completed",)):
    return round(sum(float(r[3]) for r in rs if r[1] == "C-17" and r[0][:7] == month and r[4] in sts), 1)


ans, alls, aug = tot(rows), tot(rows, sts=("completed", "cancelled", "partial")), tot(rows, "2026-08")
assert not any(r[0][:7] == "2026-09" for r in rows[: prefix_lines(text) - 1])
assert len({ans, alls, aug}) == 3
prompt = "Courier C-17 is asking about their September mileage claim. deliveries.csv has all runs since June. How many kilometres did C-17 actually drive on runs that were completed in September? I only need the total."
expect = {"expected_number": ans, "tolerance": 0.05, "expected_number_in_text": True}
finish(HERE, "tab-13312", CANARY, "tabular", "aggregate", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": 0, "TR-DECOY": alls}, "L2", {"deliveries.csv": text}, prompt, expect,
       "Sum km for one courier, one month, completed runs only, in a 2,600-row CSV.",
       '''rows = list(csv.reader(io.StringIO(case["files"]["deliveries.csv"])))
assert rows[0] == ["date", "courier", "route", "km", "status"]
print(json.dumps({"expected": round(sum(float(r[3]) for r in rows[1:] if r[1] == "C-17" and r[0][:7] == "2026-09" and r[4] == "completed"), 1)}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows by date; September begins after byte 65536 (a first-page read has no September row, answer 0).
- TR-DECOY: counting cancelled and partial runs too gives %.1f km; August for the same courier is %.1f.
## Reference solution
1. awk/data_query: courier C-17, date prefix 2026-09, status completed, sum km (1-2 calls).
## Why the answer is unique
Only status == completed counts as "completed"; answer %.1f km (tolerance 0.05).''' % (size, N, alls, aug, ans))
print("ok", size, ans, alls, aug)
