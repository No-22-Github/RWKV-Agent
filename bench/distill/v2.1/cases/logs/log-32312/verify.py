# DISTILL-CANARY-c5d831f3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'edc9de60fdb7693fb7e063f3e6470d8ef61324460673a390a9ea39a48cc8a7db', "fixture changed"
ans = sum(1 for l in files['requests.jsonl'].splitlines() if '"status": "500"' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
