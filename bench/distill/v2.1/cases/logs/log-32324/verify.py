# DISTILL-CANARY-ac7217d6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1d5a9e814cb2689c6d7842bd59b9c9656280bd01e59ba8db8484022d7d4746cb', "fixture changed"
ans = sum(1 for l in files['app.log.1'].splitlines() if ' ERROR ' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
