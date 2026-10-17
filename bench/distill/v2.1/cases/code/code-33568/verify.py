# DISTILL-CANARY-a4a5d7e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'add89c7185992eaea68175959fcb7369dd1c7ff2610e95c39a101184c3c2c349', "fixture changed"
ans = '12'
assert files['logs/jobs.log'].count(' PASSED') == 12 and ' FAILED' not in files['logs/jobs.log']

print(json.dumps({"expected_number": float(ans)}))
