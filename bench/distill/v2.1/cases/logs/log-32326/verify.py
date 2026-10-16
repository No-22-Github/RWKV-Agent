# DISTILL-CANARY-b68bfc6a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a1eaba48a00c539e375245790c3a6a93a0d2e9f7675b1bbc0f0ef7ad1ec74aa2', "fixture changed"
ans = sum(1 for l in files['logs/app-2026-09-15.log'].splitlines() if ' ERROR ' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
