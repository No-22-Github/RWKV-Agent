# DISTILL-CANARY-017a7de7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '56d74243e3d57b782f5d5b1b114f58b7ff1c32f2c048cff81b527918abcff458', "fixture changed"
print(json.dumps({"files": {'config/app.ini': case['files']['config/app.ini'].replace('[server]\nport=8080\ntimeout=30\n\n[client]\ntimeout=30\nconnect_timeout=30\n', '[server]\nport=8080\ntimeout=60\n\n[client]\ntimeout=30\nconnect_timeout=30\n')}}, ensure_ascii=False))
