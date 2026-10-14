# DISTILL-CANARY-737270a3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '11c1b5f3e4cd31b2ef103bcdd5cfcf61373af6b7ae287c7a69e5738dde0bf53c', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))
