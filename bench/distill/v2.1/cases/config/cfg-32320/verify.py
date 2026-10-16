# DISTILL-CANARY-5ba20786 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5e5e6fa4f9e64a6e4ac44d15b51a8b4529d59d132ceb3e1c4b811152462c9cc5', "fixture changed"
ans = [l.split(':')[2] for l in files['users.conf'].splitlines() if l.split(':')[0] == 'builder'][0]
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
