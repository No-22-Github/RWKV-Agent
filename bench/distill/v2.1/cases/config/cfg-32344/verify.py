# DISTILL-CANARY-216608d9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ac052551638fb0159784987d84f649617ad38c86d139072fb19e2a4db4a1a7ae', "fixture changed"
ans = sum(1 for e in __import__('json').loads(files['events.json']) if e['ts'] >= '2026-09-15T12:00:00Z')
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
