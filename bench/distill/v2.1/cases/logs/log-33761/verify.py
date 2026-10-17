# DISTILL-CANARY-d809af56 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd79a20456fd7ff49f32ede9d9b5d1569812e62d8b9d625c26df6b1d67900df92', "fixture changed"
ls=files['net.log'].splitlines()
answers=[str([k for k,l in enumerate(ls,1) if l.split()[2]=='ERROR'][0])]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
