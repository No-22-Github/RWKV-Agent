# DISTILL-CANARY-8c7ba508 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c910adce665d9c500b63dbbb377605b4d8d96f08579a32384969ac72dea4b8d4', "fixture changed"
print(json.dumps({"expected_string": [p for p in case["files"] if p.endswith("deploy.sh")][0]}))
