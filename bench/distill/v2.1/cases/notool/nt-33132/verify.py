# DISTILL-CANARY-7cb4b38a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8230081772cf04631b7de7624776b90e394b18f027c143c16970b59888e3986d', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
