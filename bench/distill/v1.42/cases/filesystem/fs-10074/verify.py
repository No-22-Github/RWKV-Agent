# DISTILL-CANARY-4c51ee33 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f850f36efe6ef63d763f24edd1f601fc12d1926cc8e80cf3bdd002aa55622cbe', "fixture changed"
README = '报表/说明.md'
RULES = ['p.endswith(".xlsx") and not p.rsplit("/", 1)[-1].startswith("~$")']
assert case["files"][README].startswith('# 报表目录')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
