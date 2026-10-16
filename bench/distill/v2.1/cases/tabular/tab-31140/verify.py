# DISTILL-CANARY-fa514597 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2aec14c345bb10a65a9fa0b93d9e27abcff956a6349c18af5140b94d451b1321', "fixture changed"
def compute(files):
    ls = [l.split() for l in files["路线/站点.txt"].strip().split("\n")]
    out = "站点,距离(公里),距上一站\n"
    prev = 0.0
    for n, d in ls:
        out += "%s,%s,%.1f\n" % (n, d, float(d) - prev)
        prev = float(d)
    return {"路线/分段.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
