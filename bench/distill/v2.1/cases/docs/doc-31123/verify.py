# DISTILL-CANARY-482c031d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '929b318c155b1b33db2b9bf9caf6a0203488c5de6fa49488bd6bf939e59a0032', "fixture changed"
def compute(files):
    ls = files["待办/杂项.txt"].strip().split("\n")
    return {"待办/清单.md": "# 待办清单\n\n" + "".join("%d. [ ] %s\n" % (i + 1, l) for i, l in enumerate(ls))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
