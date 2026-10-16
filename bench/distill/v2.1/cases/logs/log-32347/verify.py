# DISTILL-CANARY-24f56f38 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4d7ca6d565c39bb9aff327072266df9ea5da9814bd04342f5a4245d0643a2706', "fixture changed"
import json
ans = sum(1 for l in files['api.jsonl'].splitlines() if json.loads(l)['status'] >= 500)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
