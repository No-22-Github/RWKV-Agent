# DISTILL-CANARY-eaac8b95 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2a72eb6b2b734721bb80b2bd18eeb639bd29bcf87c8b1e550c334e0e624d8ed6', "fixture changed"
ans = sum(1 for l in files['gateway.log'].splitlines() if l.startswith('15/Sep/2026') and ' ERROR ' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
