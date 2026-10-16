# DISTILL-CANARY-b6f11857 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8d86a8921915654f6bd802d1feb3e5bde9a28340f2c6959fcd3a86c607bf040d', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["值班/排班.csv"].strip().split("\n")[1:]]
    d = {}
    for w, n in rows:
        d[n] = d.get(n, 0) + 1
    return {"值班/次数.txt": "".join("%s %d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
