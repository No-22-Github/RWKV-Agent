# DISTILL-CANARY-82e13bfd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a04fb982d58d376a238b7770eabf5e7ca6dca2466d50f4852ae04d19acdba814', "fixture changed"
def compute(files):
    bal = 0
    out = "日期,摘要,金额,余额\n"
    for l in files["财务/流水.csv"].strip().split("\n")[1:]:
        d, s, i, o = l.split(",")
        a = int(i) if i else -int(o)
        bal += a
        out += "%s,%s,%+d,%d\n" % (d, s, a, bal)
    return {"财务/余额表.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
