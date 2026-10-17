# DISTILL-CANARY-ff7b0d9f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1445e3d0654a5f8a76eabc0cf6100cb3b10d1a88fdd08c0d2c1eafd3795fcf4f', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
