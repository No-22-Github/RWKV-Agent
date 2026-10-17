# DISTILL-CANARY-6c29d0df : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f9e758d916fcd43a5b9606cd23ad39ad8ff1f2e040d63c43d68dc8bc4abd16de', "fixture changed"
import re
hits = [(p, i) for p, t in sorted(files.items()) for i, l in enumerate(t.split(chr(10)), 1) if re.match('^func \\(c \\*Cache\\) Evict\\(\\)', l)]
assert len(hits) == 1, hits
ans = hits[0][0]
assert hits[0][1] == 20

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
