# DISTILL-CANARY-fe1ac44f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f7da712fee5695c1d57f679e3d5708e0051cbf5b583e779485bf2c90446f8a4', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^BACKUP_KEEP_DAYS=', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 10

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
