# DISTILL-CANARY-f55daafa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
for path in ("盘点/2026Q2-差异.csv", "盘点/2026Q3-差异-初盘.csv", "盘点/2026Q3-差异.csv"):
    assert case["files"][path].startswith("SKU,库区,差异类型,差异金额"), path
rows = list(csv.DictReader(io.StringIO(case["files"]["盘点/2026Q3-差异.csv"])))
loss = round(sum(float(r["差异金额"]) for r in rows if r["差异类型"] == "盘亏"), 2)
forms = [("%.2f" % loss).rstrip("0").rstrip("."), "{:,.2f}".format(loss).rstrip("0").rstrip(".")]
ask = ["哪一份", "哪份", "哪个文件", "哪一个文件", "文件名", "路径"]
print(json.dumps({"expected_contains_any": ask + forms}, ensure_ascii=False))
