# DISTILL-CANARY-76d81d0a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5fbf13d4af920ad95951ab3750961ba7ef035d23cf18cc8e39bebb288a957665', "fixture changed"
def compute(files):
    out = "编号\t姓名\t注册日期\n"
    rows = [l.split(",") for l in files["客户/名单.csv"].strip().split("\n")[1:]]
    for i, n, d in sorted(rows, key=lambda r: int(r[0])):
        y, m, dd = d.split("-")
        out += "%04d\t%s\t%s/%s/%s\n" % (int(i), n, dd, m, y)
    return {"客户/名单.tsv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
