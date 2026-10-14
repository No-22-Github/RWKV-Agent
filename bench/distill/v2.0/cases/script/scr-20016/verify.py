# DISTILL-CANARY-12b2b325 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '973a2985a7aaecaeeaf6ac1c324589c0213781e06bfbbfbfe3d43e3bf069a8d9', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))
