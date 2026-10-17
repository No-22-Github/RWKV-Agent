# DISTILL-CANARY-55a5cc70 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ebe2ba88459374b463f85e8040ca28d5aa387e537f414f4a18753119ccf92f83', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^const EMAIL_RE\\s*=', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 9

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
