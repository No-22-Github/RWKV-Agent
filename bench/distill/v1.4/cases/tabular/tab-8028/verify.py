# DISTILL-CANARY-df8fdd83 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["订货/2026-08-望京店.csv"])))
b = list(csv.DictReader(io.StringIO(files["订货/2026-08-三里屯店.csv"])))
assert a and set(a[0]) == {"订单号", "下单日期", "品类", "件数"}
assert b and set(b[0]) == {"订单号", "下单日期", "品类", "件数"}
assert min(r["下单日期"] for r in a) >= "2026-08-01" and max(r["下单日期"] for r in a) <= "2026-08-31"
assert max(r["下单日期"] for r in b) <= "2026-08-20"
print(json.dumps({"expected_number": len(a)}))
