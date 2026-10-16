# DISTILL-CANARY-ece04f9e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'af66cfa64d9d8d6b9dd1ddfe923280c7cf2317fd5ffb23cedddd389b4bc38182', "fixture changed"
ans = sum(int(l.split(',')[2]) for l in files['sales_2026Q3.csv'].splitlines()[1:])
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
