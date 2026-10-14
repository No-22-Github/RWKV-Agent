# DISTILL-CANARY-0fabf3a0 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9c4d4d9be92a876001f3aa38bac71de2fb76743eaee6637e6541a32967706dc9', "fixture changed"
v = json.loads(case["files"]["package.json"])["dependencies"]["axios"]
print(json.dumps({"expected_string": v.lstrip("^")}))
