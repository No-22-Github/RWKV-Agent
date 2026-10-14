# DISTILL-CANARY-0236fde7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c1e9ee39cedfaa92051d08620696b78f81c0f450ebce98f19d9ccf9969293c62', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['exports/orders.csv'])))
sel = [float(r["minutes"]) for r in rows if r["status"] == "pending"]
s = round(sum(sel) / len(sel), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
