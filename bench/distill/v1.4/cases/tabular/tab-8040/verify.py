# DISTILL-CANARY-9cc88b5d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
pt = list(csv.DictReader(io.StringIO(files["财务/私教收入-9月.csv"])))
corp = list(csv.DictReader(io.StringIO(files["财务/企业团课-9月.csv"])))
assert pt and list(pt[0]) == ["日期", "项目", "金额"]
assert corp and list(corp[0]) == ["日期", "企业", "结算金额"]
assert {r["日期"] for r in pt} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
corp_days = {r["日期"] for r in corp}
assert len(corp_days) == 12 and max(corp_days) == "2026-09-12"
readme = files["财务/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 私教业务收入台账")
assert "还没导出" in readme and "补导" in readme
total = round(sum(float(r["金额"]) for r in pt), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
