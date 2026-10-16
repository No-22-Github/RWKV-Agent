# DISTILL-CANARY-e7b90723 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9aea94248346d78644c3a56397d409c2de2c94712acda53dbc993f6912c1ad70', "fixture changed"
ans = sum(1 for l in files['shipments.csv'].splitlines()[1:] if l.endswith(',DELAYED'))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
