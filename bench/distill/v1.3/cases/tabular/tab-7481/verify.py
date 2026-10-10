# DISTILL-CANARY-6b715c35 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/out-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the export carries exactly the five documented columns.
if fieldnames != ["单号", "出库日期", "商品", "规格", "件数"]:
    raise SystemExit("fixture guard failed: outbound columns are broken")

# The case premise: no passion-fruit rows exist at all.
if any("百香果" in r["商品"] for r in rows):
    raise SystemExit("fixture has 百香果 rows; the empty-filter case is broken")
items = {r["商品"] for r in rows}
if items != {"涌泉蜜桔礼箱", "阳光玫瑰葡萄", "红心猕猴桃", "高山小蜜薯"}:
    raise SystemExit("fixture guard failed: SKU set is broken")

accepted = ["百香果礼盒", "百香果 礼盒"]
print(json.dumps({"expected_contains_any": accepted}))
