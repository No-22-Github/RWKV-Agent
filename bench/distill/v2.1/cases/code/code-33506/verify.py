# DISTILL-CANARY-ba85429c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '85040d581b3afbc209b93be81edc2a85892b70c7b2786dd496c6fd0662175c1c', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^class RetryPolicy:', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 16

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
