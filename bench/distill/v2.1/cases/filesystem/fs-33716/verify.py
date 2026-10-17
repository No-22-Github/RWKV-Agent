# DISTILL-CANARY-bb32f61d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ced8f89ca29f1d91cc5d106aad108741331d0addce32d593a1caeb461fa03111', "fixture changed"
n=[p.split('/')[-1] for p in files if '.' not in p.split('/')[-1]]
answers=['Makefile']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
