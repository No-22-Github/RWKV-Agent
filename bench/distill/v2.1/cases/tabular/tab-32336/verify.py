# DISTILL-CANARY-09078308 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e596b6538afd30c5349e00925ebefc2016e3be84776c3f78b9c87296d32e8c64', "fixture changed"
ans = sum(1 for l in files['members.csv'].splitlines()[1:] if l.split(',')[2] in ('L5','L6'))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
