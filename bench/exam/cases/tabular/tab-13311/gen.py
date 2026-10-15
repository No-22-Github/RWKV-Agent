#!/usr/bin/env python3
"""Generates tab-13311 (zh, region sales total for one month excluding gift lines, 3,000-row CSV)."""
import csv, datetime, io, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, check_size, PREFIX, prefix_lines

CANARY = "EXAM-CANARY-a85e2f60"
rng = random.Random(13311)
REG = ["华东", "华南", "华北", "西南"]
SHOPS = ["上海徐汇旗舰店", "南京新街口店", "杭州西湖银泰店", "苏州工业园店", "合肥万达店", "宁波天一店"]
ITEMS = ["保温杯", "收纳盒", "台灯", "雨伞", "背包", "运动水壶", "笔记本", "充电宝"]
N = 3000
start = datetime.date(2026, 6, 1)
rows = []
for i in range(N):
    d = start + datetime.timedelta(days=int(i * 108 / N))
    typ = "赠品" if rng.random() < 0.09 else "销售"
    rows.append([d.isoformat(), rng.choice(REG), rng.choice(ITEMS), str(rng.randrange(1, 6)), "%.2f" % rng.choice([19.9, 29.5, 45.0, 59.9, 88.0, 129.0, 168.5]), typ, rng.choice(SHOPS)])
buf = io.StringIO(newline="")
w = csv.writer(buf, lineterminator="\n")
w.writerow(["日期", "区域", "商品", "数量", "单价", "类型", "门店"])
w.writerows(rows)
text = buf.getvalue()
size = check_size(text, 80_000, 200_000)


def tot(rs, month="2026-08", typ="销售"):
    return round(sum(int(r[3]) * float(r[4]) for r in rs if r[1] == "华东" and r[0][:7] == month and (typ is None or r[5] == typ)), 2)


ans, with_gift, sep = tot(rows), tot(rows, typ=None), tot(rows, "2026-09")
assert not any(r[0][:7] == "2026-08" for r in rows[: prefix_lines(text) - 1])
assert len({ans, with_gift, sep}) == 3
prompt = "销售明细.csv 是各区域从 6 月到现在的出货记录。华东区 8 月实际卖出去的东西一共多少钱？（数量乘单价，加起来；赠送的不算销售额）直接告诉我金额。"
expect = {"expected_number": ans, "tolerance": 0.01, "expected_number_in_text": True}
finish(HERE, "tab-13311", CANARY, "tabular", "aggregate", ["TR-LONG", "TR-DEFN"],
       {"TR-LONG": 0, "TR-DEFN": with_gift}, "L2", {"销售明细.csv": text}, prompt, expect,
       "Sum quantity times unit price for one region and month, excluding gift lines, in a 3,000-row CSV.",
       '''rows = list(csv.reader(io.StringIO(case["files"]["销售明细.csv"])))
assert rows[0] == ["日期", "区域", "商品", "数量", "单价", "类型", "门店"]
print(json.dumps({"expected": round(sum(int(r[3]) * float(r[4]) for r in rows[1:] if r[1] == "华东" and r[0][:7] == "2026-08" and r[5] == "销售"), 2)}))''',
       '''## Traps
- TR-LONG: %d bytes, %d rows in date order; August starts after byte 65536 (first page = June-July).
- TR-DEFN: the prompt defines sales as quantity x unit price excluding gift lines (类型=赠品). Including gift lines gives %.2f. Summing 单价 only (without quantity) is another wrong shortcut. September for the same region is %.2f.
## Reference solution
1. awk/data_query: 区域=华东, 日期 2026-08, 类型=销售, sum 数量*单价 (1-2 calls).
## Why the answer is unique
Definition is stated in the prompt; answer %.2f.''' % (size, N, with_gift, sep, ans),
       axes=["LNG", "OBS"])
print("ok", size, ans, with_gift, sep)
