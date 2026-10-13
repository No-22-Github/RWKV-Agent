# DISTILL-CANARY-90e90f1a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '24de43a0b54ab9d13879aa936e044251999e5fe3ad47c76f441d3622f6fd7e3a', "fixture changed"
README = 'src/CONTRIBUTING.md'
RULES = ['p.endswith(".py") and "/tests/" not in p', 'p.endswith(".py") and p.rsplit("/", 1)[-1].startswith("test_")']
assert case["files"][README].startswith('# Layout')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
