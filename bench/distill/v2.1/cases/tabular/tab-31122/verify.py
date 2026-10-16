# DISTILL-CANARY-bc2602a1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c94d8b0d00dea8730349eabb80aaf48925a50c2f68ea4969d1e61ea83b1c8bf9', "fixture changed"
def compute(files):
    import json
    d = json.loads(files["hr/people.json"])
    out = "dept,count,oldest\n"
    g = {}
    for p in d:
        g.setdefault(p["dept"], []).append(p)
    for k in sorted(g):
        out += "%s,%d,%s\n" % (k, len(g[k]), max(g[k], key=lambda p: p["age"])["name"])
    return {"hr/dept.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
