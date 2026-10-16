# DISTILL-CANARY-b7509ce1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e538c1279e917246a3de808ca19704c07760415dc35ef9f8feb2e6f9054f4c82', "fixture changed"
def compute(files):
    import json
    out = []
    for l in files["版本/发布.md"].strip().split("\n"):
        v, d, t = l.split(" ", 2)
        out.append({"version": v, "date": d, "note": t})
    out = out[::-1]
    return {"版本/发布.json": json.dumps(out, ensure_ascii=False, indent=2) + "\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
