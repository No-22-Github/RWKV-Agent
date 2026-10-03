# DISTILL-CANARY-6eea4b5e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
assert "94%" in case["files"]["README.md"]
rows = list(csv.DictReader(io.StringIO(case["files"]["差旅/2026-09-报销.csv"])))
d = round(round(sum(float(r["金额"]) for r in rows if r["部门"] == "市场部"), 2) * 0.94, 2)
s = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % d), s("{:,.2f}".format(d))})}))
