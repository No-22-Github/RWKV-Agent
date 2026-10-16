# DISTILL-CANARY-13e6587a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '65c21f55288b0e1bcf0972beb1e1516198f69cc874a97bfb8da3500d645fa375', "fixture changed"
def compute(files):
    n = sum(1 for l in files["运维/app.log"].split("\n") if " ERROR " in l)
    return {"运维/状态.md": files["运维/状态.md"].replace("错误数：0", "错误数：%d" % n)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
