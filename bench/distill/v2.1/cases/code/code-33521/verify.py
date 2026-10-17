# DISTILL-CANARY-2ab69cd1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4a8ccf4f838d61638eaec655b85ba5f058396ca65de0c416268911a4850366b4', "fixture changed"
import re
name = 'retry\\.Do'
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
assert sorted(out) == ['pkg/db/conn.go', 'pkg/mq/consumer.go'], out
ans = 'pkg/db/conn.go'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
