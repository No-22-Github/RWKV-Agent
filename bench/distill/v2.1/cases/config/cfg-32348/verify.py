# DISTILL-CANARY-8db4d936 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'baf239b23fc4651690cd941acd89a452cb8f7588e5f108819f6e9343f187e6d3', "fixture changed"
ans = '250'
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
