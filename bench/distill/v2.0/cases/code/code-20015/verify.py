# DISTILL-CANARY-e7e6883a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cab906ed3c44f8db3caba454fe379948c8ca9f1cb810c7b0ee6d74a8108daebd', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))
