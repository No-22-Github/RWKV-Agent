# DISTILL-CANARY-afacacc1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
gate = list(csv.DictReader(io.StringIO(files["数据/门店端-9月.csv"])))
qr = list(csv.DictReader(io.StringIO(files["数据/小程序端-9月.csv"])))
assert gate and list(gate[0]) == ["门店", "日期", "进店人次"]
assert qr and list(qr[0]) == ["门店", "日期", "进店人次"]
assert len(gate) == 120 and len(qr) == 60
# 门店端 covers all four stores on all 30 days; 小程序端 stops at 09-15.
assert {(r["门店"], r["日期"]) for r in gate} == {
    (s, "2026-09-" + str(d).zfill(2)) for s in ("滨江店", "城北店", "大学城店", "老城根店")
    for d in range(1, 31)}
assert {r["日期"] for r in qr} == {"2026-09-" + str(d).zfill(2) for d in range(1, 16)}
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 进店人次台账")
assert "尚未导出" in readme and "补录" in readme
total = sum(int(r["进店人次"]) for r in gate)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
