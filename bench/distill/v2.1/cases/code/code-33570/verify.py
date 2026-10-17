# DISTILL-CANARY-a2fbb9b9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '91a10e7db9fb578fc8c3184bb94be9e8ce5151d9c7f085c2f5fe0a1d87663ea3', "fixture changed"
ans = 'store::delete_missing'
assert 'delete_missing ... FAILED' in files['target/cargo-test.txt']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
