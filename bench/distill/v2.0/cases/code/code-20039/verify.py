# DISTILL-CANARY-52a34366 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4c26c6d848ef08e7850e7660c55878fb67299036f2f2687ba2d14318d1050337', "fixture changed"
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
