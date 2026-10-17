# DISTILL-CANARY-13c8fd6a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c5a5a8e7c6a2e1d51410dd6265570b42410d54974d26b7bf2432e6704394ccb3', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^\\tSyncInterval\\s*=', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 14

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
