# DISTILL-CANARY-1ead1066 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '71da5cfb268d92c67bfb6dd2c75968e042f94f6b5bf1b6bc55742b9c7f6da374', "fixture changed"
def compute(files):
    t = {}
    for l in files["账本/9月.csv"].strip().split("\n")[1:]:
        d, c, a = l.split(",")
        t[c] = t.get(c, 0) + float(a)
    def fmt(x):
        return ("%.2f" % x)
    out = "类别,合计\n" + "".join("%s,%s\n" % (k, fmt(t[k])) for k in sorted(t)) + "总计,%s\n" % fmt(sum(t.values()))
    return {"账本/9月汇总.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
