# DISTILL-CANARY-64c3eb22 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1b9ef0af17cae15cb5c40845859ab413817db2bc85aeb1154180fa54c90e99b7', "fixture changed"
README = 'var/README.md'
RULES = ['p.endswith(".log")']
assert case["files"][README].startswith('# var layout')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
