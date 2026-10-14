# DISTILL-CANARY-7c89e1cf : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'eaed963c2f185c86730b26825d8ed8f38439353e1efdc591a60fd030a9351ed1', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])))
s = round(sum(float(r["amount"]) for r in rows if r["category"] == "food" and r["status"] == "done"), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
