# DISTILL-CANARY-999f9f0a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["盐耗/2026-07-抄表.csv"])))
assert rows and set(rows[0]) == {"单号", "日期", "网点", "盐耗kg", "盐耗kg(估)"}
filled = [r for r in rows if r["盐耗kg"].strip()]
blank = [r for r in rows if not r["盐耗kg"].strip()]
assert filled and blank
assert all(r["盐耗kg(估)"].strip() for r in rows)
print(json.dumps({"expected_number": sum(int(r["盐耗kg"]) for r in filled)}))
