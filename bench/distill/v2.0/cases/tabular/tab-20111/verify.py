# DISTILL-CANARY-c8dd3eec : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd9cf9d3534e30c4dbf03964bc8e03adeba98f9275b6f646989f5811795db49df', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['data/orders.csv'])))
s = round(sum(float(r["金额"]) for r in rows if r["渠道"] == "官网"), 2)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
