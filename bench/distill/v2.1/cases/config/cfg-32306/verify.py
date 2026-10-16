# DISTILL-CANARY-37544b4e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '34015d8c9fb3cbeb19f5767d45f71fe7cec0ce48931883df5ea9c31ef63573a9', "fixture changed"
ans = [l.split('=')[1].strip() for l in files['relay.conf'].splitlines() if l.lower().startswith('timeout_seconds')][0]
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
