# DISTILL-CANARY-724e8147 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["数据/收银流水-9月.csv"])))
assert rows and list(rows[0]) == ["门店", "日期", "销售额"]
assert len(rows) == 70
full_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {(r["门店"], r["日期"]) for r in rows if r["门店"] != "老城根店"} == {
    (s, d) for s in ("滨江店", "城北店") for d in full_days}
old_days = {r["日期"] for r in rows if r["门店"] == "老城根店"}
assert len(old_days) == 10 and max(old_days) == "2026-09-10"
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 商品部收银台账")
assert "尚未导出" in readme and "补导" in readme
total = round(sum(float(r["销售额"]) for r in rows if r["门店"] != "老城根店"), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
