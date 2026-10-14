# DISTILL-CANARY-0b917f69 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
from decimal import Decimal, ROUND_HALF_UP
q = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)
def fm(s):
    f = ['%.2f' % s]
    f.append(f[0].rstrip('0').rstrip('.'))
    g = '{:,}'.format(int(f[0].split('.')[0])) + '.' + f[0].split('.')[1]
    return f + [g, g.rstrip('0').rstrip('.')]
a = q(Decimal('6.85') * Decimal('120.4'))
b = q(a * Decimal('1.025'))
print(json.dumps({'expected_contains_any': list(dict.fromkeys(fm(a) + fm(b)))}))
