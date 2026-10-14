# DISTILL-CANARY-02fd9424 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6bd743d0802e34f84d97692cae8d994b6cf4ada2cf1f05379947f6a8fe302807', "fixture changed"
from decimal import Decimal, ROUND_HALF_UP
q = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)
s = q(Decimal('187.40') * Decimal('1.18') / 4)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
