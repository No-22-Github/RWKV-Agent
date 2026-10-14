# DISTILL-CANARY-deec4d11 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["采购/2026-09-采购单.csv"])))
s = round(sum(float(r["金额"]) for r in rows if int(r["数量"]) >= 20), 2)
strip = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({strip("%.2f" % s), strip("{:,.2f}".format(s))})}))
