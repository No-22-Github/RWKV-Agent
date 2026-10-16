# DISTILL-CANARY-dd5a3aaf : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a1f9c78e0e11da6f34ef8ed86a8b49bdf293be677926c3a45db0adf32e1f866f', "fixture changed"
ans = sum(1 for l in files['accounts.csv'].splitlines()[1:] if l.split(',')[1].startswith('ENT'))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
