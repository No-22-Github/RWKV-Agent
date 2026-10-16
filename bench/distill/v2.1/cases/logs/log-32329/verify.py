# DISTILL-CANARY-7e9ff6b2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '31e8023ce2630be64a74f88bfb3d1714c053ed9ec46388f70cc8c70174c8dcb4', "fixture changed"
ans = sum(1 for l in files['app.err'].splitlines() if ' E1042 ' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
