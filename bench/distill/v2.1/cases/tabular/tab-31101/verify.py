# DISTILL-CANARY-c0344528 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6b082d9fcf28a322fb416dbf882020e5c47ec79b54a5714ef8e6008b6b298ab5', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["数据/门店销售.csv"].strip().split("\n")[1:]]
    tot = {}
    for s, _, a in rows:
        tot[s] = tot.get(s, 0) + int(a)
    return {"数据/门店汇总.csv": "门店,总金额\n" + "".join("%s,%d\n" % (k, tot[k]) for k in sorted(tot, key=lambda k: (-tot[k], k)))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
