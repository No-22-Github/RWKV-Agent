# DISTILL-CANARY-cd051414 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6bf3e117e088fdb0104314ef8dba53079860518343a1f13dc02e80dfedd8bdc5', "fixture changed"
from decimal import Decimal, ROUND_HALF_UP
q = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)
s = q(Decimal('12.35') * 18 + Decimal('7.8') * 26 + Decimal('129.99') * 3)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
