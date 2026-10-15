#!/usr/bin/env python3
"""Generates tab-13308 (en, count of August orders by payment method and country from a JSONL export)."""
import datetime, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX

CANARY = "EXAM-CANARY-9be3d206"
rng = random.Random(13308)
N = 1800
start = datetime.date(2026, 6, 1)
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 108 / N))
    pay = rng.choices(["card", "paypal", "gift_card", "bank_transfer"], [42, 22, 24, 12])[0]
    cc = rng.choices(["US", "CA", "GB", "DE", "AU"], [34, 26, 14, 14, 12])[0]
    st = rng.choices(["shipped", "cancelled", "pending"], [88, 8, 4])[0]
    rows.append({"id": "o-%06d" % (410000 + i), "date": d.isoformat(), "country": cc, "pay": pay,
                 "total": round(rng.uniform(9, 320), 2), "status": st})
text = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)
size = check_size(text, 80_000, 200_000)


def cnt(rs, month="2026-08"):
    return sum(1 for r in rs if r["date"][:7] == month and r["pay"] == "gift_card" and r["country"] == "CA" and r["status"] == "shipped")


ans = cnt(rows)
pre = cnt(rows[: text[:PREFIX].count("\n")])
nocancel = sum(1 for r in rows if r["date"][:7] == "2026-08" and r["pay"] == "gift_card" and r["country"] == "CA")
sep = cnt(rows, "2026-09")
assert not any(r["date"][:7] == "2026-08" for r in rows[: text[:PREFIX].count("\n")])
assert len({ans, nocancel, sep}) == 3 and ans >= 4, (ans, nocancel, sep)
prompt = "orders.jsonl is our order export for the summer. How many of the August orders paid with a gift card went to customers in Canada and actually shipped? Just the count."
expect = {"expected_number": ans, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "tab-13308", CANARY, "tabular", "filter_count", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": pre, "TR-DECOY": nocancel}, "L2", {"orders.jsonl": text}, prompt, expect,
       "Count August gift-card orders to Canada with status shipped in a 1,800-row JSONL export.",
       '''rows = [json.loads(l) for l in case["files"]["orders.jsonl"].splitlines() if l.strip()]
print(json.dumps({"expected": sum(1 for r in rows if r["date"][:7] == "2026-08" and r["pay"] == "gift_card" and r["country"] == "CA" and r["status"] == "shipped")}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows in date order; August begins after byte 65536, so a first-page read finds 0 matching orders.
- TR-DECOY: ignoring the status condition gives %d (cancelled and pending orders included); September has %d matches with the same filter.
## Reference solution
1. jq/grep style filter on date prefix 2026-08, pay gift_card, country CA, status shipped; count (1-2 calls).
## Why the answer is unique
Four exact-match conditions on enumerated fields; answer %d.''' % (size, N, nocancel, sep, ans))
print("ok", size, ans, pre, nocancel, sep)
