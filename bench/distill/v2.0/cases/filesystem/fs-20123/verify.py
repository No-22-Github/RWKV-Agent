# DISTILL-CANARY-9475061f : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9f382a1e5d3844eb3d81a95421406878972206e1d09b14e0f74c051920d3cbcd', "fixture changed"
print(json.dumps({"expected_number": sum(1 for p in case["files"] if p.startswith("backup/") and p.endswith(".tar"))}))
