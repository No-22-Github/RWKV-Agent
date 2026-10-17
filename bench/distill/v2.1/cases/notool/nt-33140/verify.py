# DISTILL-CANARY-503274b1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5c99c9537d2145124c7a7cbd5fbe7b9335e948f49b17001c5f95613ad1c86d15', "fixture changed"
assert all(t["expect"].get("tools") == [] for t in case["turns"])
print(json.dumps({"files": case["files"]}, ensure_ascii=False))
