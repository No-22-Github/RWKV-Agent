# DISTILL-CANARY-a348167c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '993a1306278665b9128320a48b951e2ced33422bd0dcb4d83613ad76046abcaf', "fixture changed"
print(json.dumps({"files": {}}))
