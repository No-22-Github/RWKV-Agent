# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6c7f097c7189379981190a04683f62d319da06c72c8b68a8511cedb6495da236', "fixture changed"
README = 'services/SECRETS.md'
RULES = ['p.rsplit("/", 1)[-1] == ".env"']
assert case["files"][README].startswith('# Secrets')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
