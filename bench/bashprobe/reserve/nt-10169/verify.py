# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8718e6d29ac86a8c7cbc4cc3a98a29dc1022c38faf89aa9059bee2ea878e2327', "fixture changed"
print(json.dumps({"expected_contains_any": ["-size +100M", "-size +100m", "-size +102400k"]}, ensure_ascii=False))
