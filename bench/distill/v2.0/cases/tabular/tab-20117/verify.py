# DISTILL-CANARY-c3fd4c59 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '834b55f82835dc272e9286913f92361b73f35b465a435787ee98157cfafbaadc', "fixture changed"
rows = [l.split(",") for l in case["files"]["成绩/期中.csv"].splitlines()[1:]]
s = round(sum(float(x[1]) for x in rows) / len(rows), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
