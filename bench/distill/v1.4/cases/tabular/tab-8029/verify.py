# DISTILL-CANARY-4b968faf : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["领用/2026-08-酵母领用.csv"])))
assert rows and set(rows[0]) == {"单号", "日期", "门店", "干酵母g", "鲜酵母g"}
filled = [r for r in rows if r["鲜酵母g"].strip()]
blank = [r for r in rows if not r["鲜酵母g"].strip()]
assert filled and blank
assert max(r["日期"] for r in filled) < "2026-08-15"
assert min(r["日期"] for r in blank) >= "2026-08-15"
g = sum(int(r["鲜酵母g"]) for r in filled)
kg = "%g" % (g / 1000)
print(json.dumps({"expected_contains_any": [str(g), "{:,}".format(g), kg + " 公斤", kg + "公斤", kg + " 千克", kg + "千克", kg + " kg"]}, ensure_ascii=False))
