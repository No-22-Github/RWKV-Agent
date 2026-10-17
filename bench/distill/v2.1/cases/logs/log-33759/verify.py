# DISTILL-CANARY-488e784b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '53b7d68a5d9469d94c3484eff5bd7422a7f0ca26002e3c9614cb014665ae765c', "fixture changed"
ls=files['app.log'].splitlines()
answers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
