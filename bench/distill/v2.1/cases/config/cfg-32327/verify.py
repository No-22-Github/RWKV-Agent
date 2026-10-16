# DISTILL-CANARY-cd194e9e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8acb5414368459f8760b40defa030377191ef8fc6f013f0fbc1fe13755f5d693', "fixture changed"
ans = '6432'
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
