# DISTILL-CANARY-54d412bc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fcbb3018a6c791f904e5ceef49e269c117315ac32d4d2cb1c41fec33ec5baeff', "fixture changed"
exp = case["expect"]["files"]
for path, rule in exp.items():
    if rule.get("unchanged"):
        assert path in case["files"], path
    if rule.get("absent"):
        assert path not in case["files"], path
assert "bash" in case["tool_policy"]["never_offer"]
assert all(t["expect"].get("forbidden_tools") for t in case["turns"])
import re
answer = sum(int(re.match(r"# size_kb: (\d+)", t).group(1)) for p, t in case["files"].items() if p.endswith(".log"))
assert str(answer) in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"files": {p: case["files"][p] for p, r in exp.items() if r.get("unchanged")}}, ensure_ascii=False))
