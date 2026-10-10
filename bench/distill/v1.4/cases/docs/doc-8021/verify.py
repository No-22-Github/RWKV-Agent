# DISTILL-CANARY-25ce520a : distillation case
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


store = files["财务/门店活动报销-9月.md"]
hq = files["财务/总部活动报销-9月.md"]
assert store.splitlines()[0] == "# 门店活动报销台账（9 月）"
assert hq.splitlines()[0] == "# 总部活动报销台账（9 月）"
store_rows = table_rows(store)
hq_rows = table_rows(hq)
assert {r[0] for r in store_rows} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {r[0] for r in hq_rows} <= {"2026-09-" + str(d).zfill(2) for d in range(1, 19)}
assert max(r[0] for r in hq_rows) == "2026-09-18"
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 财务文档库")
assert "还没同步" in readme and "补齐" in readme
total = round(sum(float(r[3]) for r in store_rows), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
