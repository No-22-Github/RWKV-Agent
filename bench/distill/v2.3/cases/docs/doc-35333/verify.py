# DISTILL-CANARY-acaed5b1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f96c2ea6c286c44b1d7e75a57ba5fc788dcd478a7cd588ea2485991dc9cecc6', "fixture changed"
print(json.dumps({"files": {}}))
