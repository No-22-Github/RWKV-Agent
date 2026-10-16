# DISTILL-CANARY-b32b63bb : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e4a32e67072f18c11cb7abd2bafdeb2c5f79a641442de141fd2a40c04c680fce', "fixture changed"
ans = len(set(l.split(',')[1] for l in files['signups.csv'].splitlines()[1:]))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
