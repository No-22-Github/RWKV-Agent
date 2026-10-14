# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6974d6eb7afb87c7fcddcda0959498b67f5d9af62ec637716a48e1b6bb7287c0', "fixture changed"
README = '文档/统计口径.md'
RULES = ['p.endswith(".md") and not p.endswith("/README.md") and not p.endswith("统计口径.md")']
assert case["files"][README].startswith('# 文档统计口径')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
