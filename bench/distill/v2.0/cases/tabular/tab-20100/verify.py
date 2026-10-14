# DISTILL-CANARY-d4765c84 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'af4310315715f766a88d091617615607dfe9be66168e3900e6b8cbc1d6ab324d', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]["data/orders.csv"])))
s = round(sum(float(r["金额"]) for r in rows if r["品类"] == "数码"), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
