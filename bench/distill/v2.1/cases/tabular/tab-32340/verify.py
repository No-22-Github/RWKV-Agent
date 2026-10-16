# DISTILL-CANARY-62e3e799 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8d5d9fc565eee5fa020ef95ddd296d41878a03535f46d930df650f0bfcdc315e', "fixture changed"
ans = '%g' % (sum(int(l.split(',')[1]) for l in files['metrics.csv'].splitlines()[1:]) / 200)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
