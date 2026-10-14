# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e13657387198ed80441cb1f7229402c5c766ed8721eb385d02b49c405540dcab', "fixture changed"
README = 'dist/NOTES.md'
RULES = ['p.endswith((".tar.gz", ".tgz"))']
assert case["files"][README].startswith('# dist/')
paths = [p for p in case["files"] if p != README]
vals = [sum(1 for p in paths if eval(rule, {"p": p})) for rule in RULES]
print(json.dumps({"expected_number": vals[-1]}))
