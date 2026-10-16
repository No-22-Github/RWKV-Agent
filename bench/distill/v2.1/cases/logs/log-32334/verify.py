# DISTILL-CANARY-d82152eb : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a232b8e5ec6c4d0a40690c2de65f62518058767db01cf4fdd8452d74d22e283b', "fixture changed"
ans = sum(1 for l in files['gateway.log'].splitlines() if 'ETIMEDOUT' in l or 'deadline exceeded' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
