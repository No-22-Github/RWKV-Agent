# DISTILL-CANARY-78718009 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dcbb8d2a9f5fbb3ecd6586164ed5aca82158adbeea9cdf59886e07a504a44d5f', "fixture changed"
rows = [l.split(",") for l in case["files"]["quote.csv"].splitlines()[1:]]
s = round(sum(int(x[1]) * float(x[2]) for x in rows), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
