#!/usr/bin/env python3
"""Generates tab-13307 (zh, sum of successfully refunded amounts in September from a 3,000-row CSV)."""
import csv, datetime, io, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX, prefix_lines

CANARY = "EXAM-CANARY-4c05f1a8"
rng = random.Random(13307)
STORES = ["朝阳店", "滨江店", "天河店", "江北店", "高新店", "古城店"]
N = 3000
start = datetime.date(2026, 6, 1)
buf = io.StringIO(newline="")
w = csv.writer(buf, lineterminator="\n")
w.writerow(["订单号", "日期", "门店", "金额", "状态"])
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 108 / N))        # 2026-06-01 .. 2026-09-16, chronological
    amt = round(rng.uniform(12, 480), 2)
    r = rng.random()
    st = "已完成" if r < 0.86 else ("已退款" if r < 0.94 else "退款失败")
    rows.append(["DD%07d" % (2600000 + i), d.isoformat(), rng.choice(STORES), "%.2f" % amt, st])
w.writerows(rows)
text = buf.getvalue()
size = check_size(text, 80_000, 200_000)


def total(rs, month, status):
    return round(sum(float(r[3]) for r in rs if r[1][:7] == month and r[4] == status), 2)


ans = total(rows, "2026-09", "已退款")
decoy = round(ans + total(rows, "2026-09", "退款失败"), 2)
pre_rows = rows[: prefix_lines(text) - 1]
assert not any(r[1].startswith("2026-09") for r in pre_rows)          # no September data in the first 64KB
assert ans != decoy
prompt = "订单导出.csv 是门店订单从 6 月到现在的全部流水。9 月份退款成功的订单一共退了多少钱？告诉我最后的金额就行。"
expect = {"expected_number": ans, "tolerance": 0.01, "expected_number_in_text": True}
finish(HERE, "tab-13307", CANARY, "tabular", "aggregate", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": 0, "TR-DECOY": decoy}, "L2", {"订单导出.csv": text}, prompt, expect,
       "Sum the successfully refunded amounts of one month in a 3,000-row order CSV.",
       '''rows = list(csv.reader(io.StringIO(case["files"]["订单导出.csv"])))
assert rows[0] == ["订单号", "日期", "门店", "金额", "状态"]
print(json.dumps({"expected": round(sum(float(r[3]) for r in rows[1:] if r[1][:7] == "2026-09" and r[4] == "已退款"), 2)}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows, chronological; all of September starts after the first 64KB (first page has June-July only: September total from a prefix read is 0).
- TR-DECOY: status 退款失败 (refund failed) rows in September are a different, similar-looking status; adding them gives %.2f. August refunds are also present.
## Reference solution
1. data_query / awk: filter date starts with 2026-09 and 状态 == 已退款, sum 金额 (1-2 calls).
## Why the answer is unique
"退款成功" maps to the single status value 已退款; September = date prefix 2026-09; answer %.2f.''' % (size, N, decoy, ans))
print("ok", size, ans, decoy)
