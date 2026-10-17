# DISTILL-CANARY-91459496 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '511221a497c3884e0febf7b74b356ab4c3e9f44aba9f7c0e3105eaa287ac2d96', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^export function isRateLimited\\(', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 16

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
