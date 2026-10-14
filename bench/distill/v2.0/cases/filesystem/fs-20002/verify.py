# DISTILL-CANARY-c3d60307 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8bf258e7eabc611f30c782593f8ad1272786f5fcf2ed691bbd47b4d15295e769', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
answer = sum(1 for p in case["files"] if p.startswith("build/"))
assert str(answer) in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))
