# DISTILL-CANARY-719f6ebe : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6d6404c2b9b75a59eca583b070064ea0b83af883f83894cb386ebd8d9b70613e', "fixture changed"
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
ans = count('TODO', inc=('shop/',))
assert str(ans) == '4', ans

print(json.dumps({"expected_number": float(ans)}))
