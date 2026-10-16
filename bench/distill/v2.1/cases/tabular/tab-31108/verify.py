# DISTILL-CANARY-377225ae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '920f9ea250a5a06b7d7586fe0752d3fcb946e34195815af13994946dff648657', "fixture changed"
def compute(files):
    s = {}
    for fn, sg in (("库存/入库.csv", 1), ("库存/出库.csv", -1)):
        for l in files[fn].strip().split("\n")[1:]:
            k, q = l.split(",")
            s[k] = s.get(k, 0) + sg * int(q)
    return {"库存/结存.csv": "sku,结存\n" + "".join("%s,%d\n" % (k, s[k]) for k in sorted(s))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
