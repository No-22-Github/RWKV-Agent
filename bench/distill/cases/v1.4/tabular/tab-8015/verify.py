# DISTILL-CANARY-0b10c36f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
fx = json.loads(case["files"]["rates/fx-2026-09.json"])
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/sept.csv"])))
c = round(sum(float(r["amount"]) for r in rows if r["currency"] == "EUR") * fx["EUR_CNY"], 2)
s = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % c), s("{:,.2f}".format(c))})}))
