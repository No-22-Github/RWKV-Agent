# DISTILL-CANARY-67c3d560 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '02942d09d97daf2018d7db11e509bfd67c42b1a9485987c6c8211c67f17ac308', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['data/orders.csv'])))
sel = [float(r["时长分钟"]) for r in rows if r["渠道"] == "电话"]
s = round(sum(sel) / len(sel), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
