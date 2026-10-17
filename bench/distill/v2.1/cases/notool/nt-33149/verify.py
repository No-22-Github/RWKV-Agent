# DISTILL-CANARY-62727cc9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f00d922e6ab3ae03f3161c48905ca4757cf92d936645ed81340d91d6384df3e2', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
