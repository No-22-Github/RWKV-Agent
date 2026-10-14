# DISTILL-CANARY-e2127a73 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4f8f58727965a89e4834ce8e56d8180bfc6d908a82e3137527e482d3807d3b9b', "fixture changed"
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
