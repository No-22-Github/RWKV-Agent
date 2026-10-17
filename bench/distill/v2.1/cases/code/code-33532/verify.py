# DISTILL-CANARY-e014ed1e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '79f9832362d251be65518a809e3d45e584bc58cd246a23442d0b3a76c7a15d6e', "fixture changed"
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
ans = sum(v for p, v in count('FIXME', inc=('mon/',), per=True).items() if p.endswith('.py'))
assert str(ans) == '4', ans

print(json.dumps({"expected_number": float(ans)}))
