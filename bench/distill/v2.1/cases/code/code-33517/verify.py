# DISTILL-CANARY-a3decb7b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '048e0b6bd4803b74152058f6571b70321d6c841cd808117ad3e8b59d0801ad28', "fixture changed"
import re
name = 'fmtMoney'
out = []
for p, t in sorted(files.items()):
    for l in t.split(chr(10)):
        s = l.strip()
        if s.startswith(('#', '//', '*', '/*')) or re.match(r'(export )?(async )?(def|func|function) ', s):
            continue
        s = re.sub(r"(\"[^\"]*\"|'[^']*')", '', s)
        if re.search(r'\b' + name + r'\(', s):
            out.append(p)
            break
assert sorted(out) == ['src/views/cart.ts', 'src/views/receipt.ts'], out
ans = 'src/views/cart.ts'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
