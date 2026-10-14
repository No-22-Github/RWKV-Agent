# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fa13e04d9f1fa883ad902722ceec8ce77a3260352d5162ff1810a60483973d0f', "fixture changed"
README = '相册/说明.txt'
RULES = ['p.lower().endswith((".jpg", ".jpeg")) and "/.thumbs/" not in p']
assert case["files"][README].startswith('相册整理规则')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
