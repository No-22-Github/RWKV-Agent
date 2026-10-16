# DISTILL-CANARY-44dbbc81 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '42979e916378555e3dd66368868b7d0a2fbe833cbc6ef193bb008b55e36a11b8', "fixture changed"
ans = str(max(int(l.split(',')[1]) for l in files['scores.csv'].splitlines()[1:]))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
