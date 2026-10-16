# DISTILL-CANARY-05a994d6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a0993e55ee5c2bf3c1306aa7bc02ba667d8576f50940a6e047e47505e006c5e9', "fixture changed"
def compute(files):
    d = {}
    for l in files["price/discount.txt"].strip().split("\n"):
        k, v = l.split()
        d[k] = int(v[:-1])
    out = "item,original,final\n"
    for l in files["price/list.csv"].strip().split("\n")[1:]:
        k, p = l.split(",")
        fin = float(p) * (100 - d.get(k, 0)) / 100
        out += "%s,%s,%.2f\n" % (k, p, fin)
    return {"price/final.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
