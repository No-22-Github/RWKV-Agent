# DISTILL-CANARY-905bb48f : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1b66aedbcfdcd78f0117731401d0fb173073173391bf5148739f00c28a10cc3c', "fixture changed"
print(json.dumps({"expected_string": '# Getting Started'}, ensure_ascii=False))
