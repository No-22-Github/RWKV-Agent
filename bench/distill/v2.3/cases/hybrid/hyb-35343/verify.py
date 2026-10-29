# DISTILL-CANARY-0da15433 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0b3c16c040a81af8e97db82186d0664a223e6c955580900471cbf4f8c2230579', "fixture changed"
print(json.dumps({"files": {}}))
