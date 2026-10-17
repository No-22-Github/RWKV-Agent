# DISTILL-CANARY-01eecedd : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0a042c87d2ff5690865d0e65dfb4acc20cb6d6eee547b3f5015865b679789c70', "fixture changed"
import re
def count(word, inc=('',), exc=(), per=False):
    n = {}
    for p, t in sorted(files.items()):
        if not p.startswith(tuple(inc)) or (exc and p.startswith(tuple(exc))):
            continue
        for l in t.split(chr(10)):
            if re.search(r'(#|//|/\*|^\s*\*|--|;)\s*' + word + r'\b', l):
                n[p] = n.get(p, 0) + 1
    return n if per else sum(n.values())
ans = sorted(count('TODO', exc=('README',), per=True))
assert ans == ['scripts/run.sh', 'svc/job.go'], ans
ans = 'svc/job.go'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
