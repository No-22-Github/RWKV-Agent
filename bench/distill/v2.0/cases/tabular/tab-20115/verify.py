# DISTILL-CANARY-ac4a964a : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3312451c934aa4a85514fadc558f25d9f604007002d8c17e0a2c008a3dba8838', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['exports/orders.csv'])))
b = max(rows, key=lambda r: float(r["amount"]))
print(json.dumps({"expected_string": b["order_id"]}))
