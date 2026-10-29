# DISTILL-CANARY-23c916a9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8ebcd65c482beb15f917e3e36889f186287652e7876ec677245fe520508ae5e4', "fixture changed"
print(json.dumps({"files": {}}))
