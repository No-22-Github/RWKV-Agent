# DISTILL-CANARY-d9ecddd8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2654bfb93fa21a086026e2e7867daa9bd25c9ff5fb5f2a486f921b5a2fcfa015', "fixture changed"
exp = case["expect"]["files"]
assert all(r.get("unchanged") and p in case["files"] for p, r in exp.items())
assert "bash" in case["turns"][0]["expect"]["required_tools"]
assert all(set(t["expect"]["required_tools"]) <= set(case["tool_policy"]["must_offer"]) for t in case["turns"])
print(json.dumps({"files": {p: case["files"][p] for p in exp}}, ensure_ascii=False))
