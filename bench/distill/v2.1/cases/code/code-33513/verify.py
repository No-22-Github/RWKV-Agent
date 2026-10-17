# DISTILL-CANARY-d6194d1c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f177b79e676fcb0615a12c231bfec48b57b56dcd666b30b79fe520b05cdbf94e', "fixture changed"
import re
name = 'apply_vat'
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
assert sorted(out) == ['billing/invoice.py', 'billing/refund.py'], out
ans = 'billing/invoice.py'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
