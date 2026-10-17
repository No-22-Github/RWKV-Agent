# DISTILL-CANARY-4f6c2aa2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1c5f3104fdf95e1643ea51ad24cd6a145e2e02e679d588036088de384d128a3f', "fixture changed"
ns = {}
for p in ['ship/rates.py', 'ship/fee.py']:
    exec(files[p].replace('from ship.rates import *', ''), ns)
ans = str(eval('int(shipping_fee(8, 120))', ns))
assert str(ans) == '16', ans

print(json.dumps({"expected_number": float(ans)}))
