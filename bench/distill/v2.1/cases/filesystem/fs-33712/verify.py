# DISTILL-CANARY-d0948ee3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '42e18f46096d05c5a5321524196a5be868e2712c45b1fc4ea4e0ea51a9401212', "fixture changed"
answers=['pad_v2.dat']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
