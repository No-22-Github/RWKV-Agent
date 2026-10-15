#!/usr/bin/env python3
"""Generates tab-13309 (zh, filter-count on a 2,400-row ticket CSV)."""
import csv, datetime, io, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX, prefix_lines

CANARY = "EXAM-CANARY-2d7a8e51"
rng = random.Random(13309)
N = 2400
start = datetime.date(2026, 6, 1)
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 108 / N))
    pri = rng.choices(["P1", "P2", "P3"], [20, 35, 45])[0]
    hrs = rng.choice([48, 48, 48]) if rng.random() < 0.06 else rng.randrange(1, 120)
    st = rng.choices(["已关闭", "处理中", "待分配"], [78, 14, 8])[0]
    rows.append(["TK%06d" % (88000 + i), d.isoformat(), rng.choice(["网络", "账号", "打印机", "邮箱", "权限"]), pri, str(hrs), st])
buf = io.StringIO(newline="")
w = csv.writer(buf, lineterminator="\n")
w.writerow(["工单号", "创建日期", "类型", "优先级", "处理时长(小时)", "状态"])
w.writerows(rows)
text = buf.getvalue()
size = check_size(text, 80_000, 200_000)


def cnt(rs, ge=False, closed=True):
    return sum(1 for r in rs if r[1][:7] == "2026-09" and r[3] == "P1" and (r[5] == "已关闭" or not closed)
               and (int(r[4]) >= 48 if ge else int(r[4]) > 48))


ans, ge, anyst = cnt(rows), cnt(rows, ge=True), cnt(rows, closed=False)
assert not any(r[1][:7] == "2026-09" for r in rows[: prefix_lines(text) - 1])
assert len({ans, ge, anyst}) == 3, (ans, ge, anyst)
prompt = "工单导出.csv 是 IT 支持组这个夏天的工单。9 月份创建的 P1 工单里，已经关闭、而且处理时间超过 48 小时的有几张？"
expect = {"expected_number": ans, "tolerance": 0.001, "expected_number_in_text": True}
finish(HERE, "tab-13309", CANARY, "tabular", "filter_count", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": 0, "TR-DECOY": ge}, "L2", {"工单导出.csv": text}, prompt, expect,
       "Count September P1 closed tickets handled for more than 48 hours in a 2,400-row CSV.",
       '''rows = list(csv.reader(io.StringIO(case["files"]["工单导出.csv"])))
assert rows[0][0] == "工单号"
print(json.dumps({"expected": sum(1 for r in rows[1:] if r[1][:7] == "2026-09" and r[3] == "P1" and r[5] == "已关闭" and int(r[4]) > 48)}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows by creation date; September rows start after byte 65536 (a first-page read sees none, answer would look like 0).
- TR-DECOY: tickets with exactly 48 hours exist (about 6%% of rows); counting >=48 gives %d. Ignoring the 已关闭 condition gives %d.
## Reference solution
1. awk/data_query: date prefix 2026-09, 优先级 P1, 状态 已关闭, 处理时长 > 48; count (1-2 calls).
## Why the answer is unique
"超过 48" is strictly greater; answer %d.''' % (size, N, ge, anyst, ans))
print("ok", size, ans, ge, anyst)
