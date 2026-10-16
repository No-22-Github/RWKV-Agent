# DISTILL-CANARY-24166b3e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'db20d96748a680a5d43bdaf1c43ffc482b3210fb7d17e2a5ae8bb33e509aa326', "fixture changed"
ans = sum(1 for l in files['staff.txt'].splitlines()[1:] if l.split('|')[2] == '研发')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
