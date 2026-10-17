# DISTILL-CANARY-9430fa14 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ae74e2a0ba7ef03a047565c46e3dc6f74845c40a1879672d1c1bcef27f5df921', "fixture changed"
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
ans = count('TODO', inc=('ring/ring.go', 'ring/peer.go'))
assert str(ans) == '4', ans

print(json.dumps({"expected_number": float(ans)}))
