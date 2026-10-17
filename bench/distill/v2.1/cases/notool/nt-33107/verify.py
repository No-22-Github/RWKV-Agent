# DISTILL-CANARY-f970a111 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e8019f9f2188067a3f9fff15b977fd5355b94b3ef8c259fe3f2555dd5dacec8a', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
