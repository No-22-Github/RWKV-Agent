# DISTILL-CANARY-0f9aa25f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0841e712a48b7d3284d06e1f8b75b91a2b8125ed4b2c734d4fb3434a7525bd45', "fixture changed"
README = '数据/说明.md'
RULES = ['p.endswith(".csv")', 'p.endswith(".csv") and "2025" in p.rsplit("/", 1)[-1]']
assert case["files"][README].startswith('# 数据目录')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
