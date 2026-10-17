# DISTILL-CANARY-ced52237 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dd58f1a5eb751d7b4e48cc970466eaf56ee8a2da1196a62d2a4f72f5cbea473d', "fixture changed"
ls=files['worker.log'].splitlines()
answers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l or ' FATAL ' in l][0]), str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
