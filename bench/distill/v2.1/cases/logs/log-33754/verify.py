# DISTILL-CANARY-425e3df5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '54762384b644df0e6779d1cae87601d7b629cf0c2b81976a426431d52d692f6a', "fixture changed"
ls=files['svc.log'].splitlines()
i=[k for k,l in enumerate(ls,1) if ' ERROR ' in l][0]
answers=[str(i)]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
