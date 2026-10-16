# DISTILL-CANARY-c7bec185 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1d53588c7d2593320b6697448e663134867fec3467a8945b5054ea5bab2befbf', "fixture changed"
ans = len(set(l.split(' from ')[1].split()[0] for l in files['access.log'].splitlines()))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
