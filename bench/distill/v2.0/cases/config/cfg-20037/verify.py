# DISTILL-CANARY-d140aa2e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ed103a33f6c1c09a6ab5e22236f43b349833c954635ec28bfc5f8e73e9ee8d51', "fixture changed"
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
