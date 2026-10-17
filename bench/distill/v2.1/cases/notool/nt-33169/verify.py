# DISTILL-CANARY-8b956313 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd4e83ea94d10d741cd8eb52d96be95fffadf25574732e13986b49bb1e7310575', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
