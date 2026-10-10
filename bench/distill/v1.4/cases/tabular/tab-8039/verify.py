# DISTILL-CANARY-12ec9bea : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
inst = list(csv.DictReader(io.StringIO(files["数据/到店消课-9月.csv"])))
on = list(csv.DictReader(io.StringIO(files["数据/线上私教-9月.csv"])))
assert inst and list(inst[0]) == ["日期", "教练", "消课分钟"]
assert on and list(on[0]) == ["日期", "教练", "消课分钟"]
assert len({(r["教练"], r["日期"]) for r in inst}) >= 85
inst_days = {r["日期"] for r in inst}
assert inst_days == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
on_days = {r["日期"] for r in on}
assert on_days <= {"2026-09-" + str(d).zfill(2) for d in range(1, 15)} and len(on) >= 8
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 私教消课台账")
assert "还没同步" in readme and "10 月 8 日" in readme
total = sum(int(r["消课分钟"]) for r in inst)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
