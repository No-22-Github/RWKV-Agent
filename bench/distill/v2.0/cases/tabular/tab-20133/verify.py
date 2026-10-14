# DISTILL-CANARY-5b28cb83 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
from decimal import Decimal, ROUND_HALF_UP
q = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)
s = q(Decimal(7850) * Decimal('1.06') / 12)
f = ["%.2f" % s]
f.append(f[0].rstrip("0").rstrip("."))
g = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]
f += [g, g.rstrip("0").rstrip(".")]
print(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))
