# DISTILL-CANARY-54087ef6 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2b61d553ab889dd845fa2db3a06d779c6c6e32addccc4d02d000c79783eddaef', "fixture changed"
rows = [l.split(",") for l in case["files"]["hr/salaries.csv"].splitlines()[1:]]
sel = [int(x[2]) for x in rows if x[1] == "ops"]
s = round(sum(sel) / len(sel), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
