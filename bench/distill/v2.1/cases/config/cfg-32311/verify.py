# DISTILL-CANARY-9dbdeabb : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c0f0db57e0558a9f82c2e246450b61ab3196ac6f66f62a6e72a5d538cce815a6', "fixture changed"
ans = sum(1 for l in files['features.conf'].splitlines() if '=' in l and l.split('=')[1].strip() in ('On','Enabled','Yes'))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
