# DISTILL-CANARY-41db07d0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b428c7d406a55b789ae90bb3702152b26def97495b6a0249f973cb1adfa569a9', "fixture changed"
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert all("bash" in t["expect"]["required_tools"] for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
