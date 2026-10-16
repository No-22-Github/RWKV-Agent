# DISTILL-CANARY-07652997 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'feeed87a8a939c8671e9127586da4684309cfe4262d4f3dd2a3a9bd6c1555854', "fixture changed"
ans = sum(1 for l in files['customers.csv'].splitlines()[1:] if l.split(',')[2].strip() == '华南')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
