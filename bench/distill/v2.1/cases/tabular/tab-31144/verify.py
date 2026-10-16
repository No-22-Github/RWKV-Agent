# DISTILL-CANARY-ebdd06fe : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8c96e7de524e0332d1cf14581eb4cc5dc4f0b1e3f2f9149fc64c13c64f09c0f7', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["问卷/回答.csv"].strip().split("\n")[1:]]
    low = [r for r in rows if int(r[1]) <= 3]
    return {"问卷/跟进.csv": "编号,满意度,建议\n" + "".join(",".join(r) + "\n" for r in sorted(low, key=lambda r: (int(r[1]), int(r[0]))))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
