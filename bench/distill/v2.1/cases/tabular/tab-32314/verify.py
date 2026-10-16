# DISTILL-CANARY-e4034c3d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '58cfaa26c16f263a5d797d0e93060789ebd40d55e2caa4b039d745e949ae4d4e', "fixture changed"
ans = sum(int(l.split(';')[2]) for l in files['stock.csv'].splitlines()[1:] if l.split(';')[1] == 'Gdansk')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
