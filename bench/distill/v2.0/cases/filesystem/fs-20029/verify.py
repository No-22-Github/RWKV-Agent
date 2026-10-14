# DISTILL-CANARY-7759284d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '170a42e1359336fdfc58f3dfb6931c99647db020afa4e1930a0f109f90ddd082', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged") or "equals" in rule:
        assert path in case["files"] or "equals" in rule, path
    if rule.get("absent"):
        assert path in case["files"], path
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
assert "bash" in case["tool_policy"]["must_offer"]
print(json.dumps({"files": {p: (r["equals"] if "equals" in r else case["files"][p]) for p, r in exp.items() if not r.get("absent")}}, ensure_ascii=False))
