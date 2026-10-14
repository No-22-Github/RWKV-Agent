# DISTILL-CANARY-02864833 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1a283ebeee5ba521955264418d3793a08e62b66e8bb26517113c3fc50be4ea3e', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['data/orders.csv'])))
c = {}
for r in rows:
    c[r["品类"]] = c.get(r["品类"], 0) + 1
print(json.dumps({"expected_string": max(c, key=c.get)}, ensure_ascii=False))
