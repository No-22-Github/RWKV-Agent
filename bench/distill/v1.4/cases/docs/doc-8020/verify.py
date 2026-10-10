# DISTILL-CANARY-bb728090 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "日期":
                continue
            rows.append(cells)
    return rows


own = files["行政/门店自购器材登记-9月.md"]
cen = files["行政/总部采购入库登记-9月.md"]
assert own.splitlines()[0] == "# 门店自购器材登记（9 月）"
assert cen.splitlines()[0] == "# 总部集中采购入库登记（9 月）"
own_rows = table_rows(own)
cen_rows = table_rows(cen)
all_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
cen_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 23)}
assert {r[0] for r in own_rows} == all_days
assert {r[0] for r in cen_rows} == cen_days
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 行政文档库")
assert "还没导回" in readme and "补齐" in readme
total = sum(int(r[3]) for r in own_rows)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
