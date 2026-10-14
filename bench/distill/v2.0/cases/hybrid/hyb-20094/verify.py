# DISTILL-CANARY-c39cacf3 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'adf6e1184331c6e532d7f5f2e5556de4dd1831a8073e546dcd07db504b2fae5f', "fixture changed"
m = re.search(r"周六：(\S+)", case["files"]["行程.md"])
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
