# DISTILL-CANARY-e9ec0ed4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2fe081fcac880286eb58db3ec455580cbd18e351bb22c77e5e7f5c4f822fd1e1', "fixture changed"
def compute(files):
    d = {}
    for l in files["销量/月度.csv"].strip().split("\n")[1:]:
        m, p, n = l.split(",")
        d[p] = d.get(p, 0) + int(n)
    return {"销量/产品合计.csv": "产品,Total\n" + "".join("%s,%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
