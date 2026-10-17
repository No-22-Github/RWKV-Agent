# DISTILL-CANARY-498e65ca : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7229d5eac04c9ab966f58c18403bb6021e429d5c1decc91772875ee702e2d1a9', "fixture changed"
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
ans = count('TODO', inc=('src/',))
assert str(ans) == '4', ans

print(json.dumps({"expected_number": float(ans)}))
