# DISTILL-CANARY-ec0d2ff9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cc4d6a6cb6194bb5ab2a39fcf902a28388c48f242d3cac78ec13bd661e514fae', "fixture changed"
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
ans = sum(len([1 for l in t.split(chr(10)) if re.search(r'(#|//)\s*TODO\(lena\)', l)]) for p, t in files.items() if not p.endswith('.md'))
assert str(ans) == '4', ans

print(json.dumps({"expected_number": float(ans)}))
