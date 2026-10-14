# DISTILL-CANARY-93d872db : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c436bef84bab5e5dfb8e17a58d1b3544f3d71358c5087f589113aa7c5505faad', "fixture changed"
rows = [l.split(",") for l in case["files"]["data/月度开销.csv"].splitlines()[1:]]
s = round(sum(float(x[1]) for x in rows), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
