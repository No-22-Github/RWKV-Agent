# DISTILL-CANARY-8a134498 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6c30a05b55d0416c8bc0cc0923328240bbd53a6fd9247314fc75deb15270c5e6', "fixture changed"
answers=['conf/prod/app.ini']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
