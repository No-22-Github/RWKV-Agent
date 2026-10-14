# DISTILL-CANARY-51687b53 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f6dc8402b1f3ecc142a5322710f295a3daa567bd4964f3cab9daa8a5047ce83', "fixture changed"
print(json.dumps({"expected_string": re.findall(r"^\d+\. (.+)$", case["files"]["trip.md"], re.M)[-1]}))
