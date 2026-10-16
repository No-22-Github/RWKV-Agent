# DISTILL-CANARY-0e426b21 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '28135abfcec2066b63716e0364e3989001772a8e83d0e44108abe607b487a5e0', "fixture changed"
ans = sum(1 for l in files['worker.log'].splitlines() if '[warn]' in l)
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
