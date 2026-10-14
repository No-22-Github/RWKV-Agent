# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c59e32de494ce63ccd815398ccf7e2be8d6f3f952eef5453182dc83da9740129', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["华南"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
