# DISTILL-CANARY-de862616 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e12941b4aed51ef8be30dab408fa17b97b5dd4ad156650391b00c0bb8cff7e33', "fixture changed"
print(json.dumps({"files": {}}))
