#!/usr/bin/env python3
"""Generates tab-13310 (en, store with most returns in Q3 from a 3,600-row CSV)."""
import csv, datetime, io, random, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX

CANARY = "EXAM-CANARY-c3f81b94"
rng = random.Random(13310)
STORES = ["Harbor Point", "Eastgate Mall", "Old Town", "Riverside", "Northfield"]
N = 3600
start = datetime.date(2026, 4, 1)          # Apr 1 .. Sep 16 (168 days)
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 168 / N))
    early = d < datetime.date(2026, 7, 1)
    st = rng.choices(STORES, [30, 20, 18, 17, 15])[0]
    rp = 0.08
    if st == "Harbor Point" and early:
        rp = 0.30
    if st == "Eastgate Mall" and not early:
        rp = 0.22
    typ = "return" if rng.random() < rp else "sale"
    rows.append([d.isoformat(), st, "SKU-%04d" % rng.randrange(1000, 4200), str(rng.randrange(1, 5)), "%.2f" % rng.uniform(4, 90), typ])
buf = io.StringIO(newline="")
w = csv.writer(buf, lineterminator="\n")
w.writerow(["date", "store", "sku", "qty", "unit_price", "type"])
w.writerows(rows)
text = buf.getvalue()
size = check_size(text, 80_000, 200_000)


def top(rs, lo, hi, by="count"):
    c = Counter()
    for r in rs:
        if lo <= r[0] <= hi and r[5] == "return":
            c[r[1]] += 1
    return c.most_common(2)


q3 = top(rows, "2026-07-01", "2026-09-30")
allr = top(rows, "2026-04-01", "2026-09-30")
rev = Counter()
for r in rows:
    if "2026-07-01" <= r[0] and r[5] == "sale":
        rev[r[1]] += int(r[3]) * float(r[4])
pre = Counter(r[1] for r in rows[: text[:PREFIX].count("\n") - 1] if r[5] == "return").most_common(2)
assert q3[0][0] == "Eastgate Mall" and q3[0][1] > q3[1][1] + 5, q3
assert allr[0][0] != "Eastgate Mall" and pre[0][0] != "Eastgate Mall", (allr, pre)
assert rev.most_common(1)[0][0] != "Eastgate Mall"
prompt = "I'm putting together the Q3 retail review. returns-log.csv has every sale and return line for the stores since April. Which store had the most returns in Q3 (July through September)? Just the store name."
expect = {"output_contains_any": ["Eastgate Mall", "Eastgate"], "output_contains_any_token": True}
finish(HERE, "tab-13310", CANARY, "tabular", "rank", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": pre[0][0], "TR-DECOY": allr[0][0]}, "L2", {"returns-log.csv": text}, prompt, expect,
       "Rank stores by Q3 return lines in a 3,600-row CSV that starts in April.",
       '''rows = list(csv.reader(io.StringIO(case["files"]["returns-log.csv"])))
assert rows[0] == ["date", "store", "sku", "qty", "unit_price", "type"]
c = {}
for r in rows[1:]:
    if "2026-07-01" <= r[0] <= "2026-09-30" and r[5] == "return":
        c[r[1]] = c.get(r[1], 0) + 1
best = sorted(c.items(), key=lambda kv: -kv[1])
assert best[0][1] > best[1][1]
print(json.dumps({"expected_contains_any": [best[0][0], best[0][0].split()[0]]}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows from April; a first-page read covers April to about mid June and points to %s.
- TR-DECOY: ranking returns over the whole file (April-September) gives %s; the store with the highest Q3 sales revenue is %s. Only returns in July-September count.
## Reference solution
1. awk/data_query: filter type == return and date in Q3, count per store, take max (1-2 calls).
## Why the answer is unique
Counting return lines (the file has one line per item row); Eastgate Mall leads Q3 with %d vs %d for %s.''' % (size, N, pre[0][0], allr[0][0], rev.most_common(1)[0][0], q3[0][1], q3[1][1], q3[1][0]))
print("ok", size, q3, allr, pre)
