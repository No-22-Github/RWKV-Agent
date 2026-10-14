# DISTILL-CANARY-22c34392 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'da59ba8c53633bbc98649febb11d3e0ff484d693352688e95080bae927f2fb50', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])))
print(json.dumps({"expected_number": sum(1 for r in rows if r["channel"] == "web" and r["status"] == "cancelled")}))
