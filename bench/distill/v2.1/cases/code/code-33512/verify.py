# DISTILL-CANARY-01121aa6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ed46cfb80a7a6db65b824c74df6b9faf6223a23e65385b72534d94a2ac15456e', "fixture changed"
lines = files['src/status.ts'].split(chr(10))
idx = [i for i, l in enumerate(lines, 1) if 'Cancelled = 9' in l]
ans = 'src/status.ts'
assert idx == [7]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
