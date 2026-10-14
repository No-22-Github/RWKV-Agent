# DISTILL-CANARY-f733b0a6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7537b46c7f6c670150e3e654fc2b26de2548c05a6e7a78b8e9d64b0c4935f090', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged") or "equals" in rule:
        assert path in case["files"] or "equals" in rule, path
    if rule.get("absent"):
        assert path in case["files"], path
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
assert "bash" in case["tool_policy"]["must_offer"]
print(json.dumps({"files": {p: (r["equals"] if "equals" in r else case["files"][p]) for p, r in exp.items() if not r.get("absent")}}, ensure_ascii=False))
