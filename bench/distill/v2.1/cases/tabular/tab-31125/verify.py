# DISTILL-CANARY-5d3ac224 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '549580cb144de41d43b78f740c2b95ca1f13c7f008d9eb776a1647512ccca842', "fixture changed"
def compute(files):
    import json
    out = []
    for l in files["销售/订单.csv"].strip().split("\n")[1:]:
        o, c, t = l.split(",")
        out.append({"order": o, "customer": c, "total": float(t)})
    return {"销售/订单.json": json.dumps(out, ensure_ascii=False, indent=2) + "\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
