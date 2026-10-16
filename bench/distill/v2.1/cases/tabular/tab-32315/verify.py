# DISTILL-CANARY-8805dad3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'eb9a17f4e3bc1756acc118a7402284f9c2ec75c662db46ba826adde36ab5ec70', "fixture changed"
ans = sum(1 for l in files['orders_q3.csv'].splitlines()[1:] if l.split(',')[2] == 'Ines Marchetti')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
