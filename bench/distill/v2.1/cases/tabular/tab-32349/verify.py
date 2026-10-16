# DISTILL-CANARY-00ca6ac7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a955da01e3f68ee1835f978631acaa920b66d6e5c5fbc2ef9d0597ba98ae216c', "fixture changed"
ans = sum(int(l.split(',')[2]) for l in files['revenue.csv'].splitlines()[1:] if l.split(',')[1] == '华南')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
