# DISTILL-CANARY-94236597 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a11e5696c9dfd5e4b411f8a092fe7507014e8e00181b75e6c7fbb5a6ebb7a005', "fixture changed"
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
ans = max(count('FIXME', inc=('api/',), per=True).items(), key=lambda kv: (kv[1], kv[0]))
assert ans == ('api/orders.js', 5), ans
ans = 'api/orders.js'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
