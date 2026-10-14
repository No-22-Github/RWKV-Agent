# DISTILL-CANARY-59eddc4f : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '25d75d22fcef49c436715f001720fa7537da57ed07af3b08667b793a6697abd3', "fixture changed"
from decimal import Decimal, ROUND_HALF_UP
q = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)
s = q(Decimal('898.5') * Decimal('0.85') - 30)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
