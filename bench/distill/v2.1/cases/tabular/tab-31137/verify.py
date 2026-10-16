# DISTILL-CANARY-844ea312 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7c8d8bbfd61799e447370e63ecd0b665ede5bc2a29482d708d97ff5873675baf', "fixture changed"
def compute(files):
    out = "品名,数量,单价,小计\n"
    tot = 0
    for l in files["采购/需求.csv"].strip().split("\n")[1:]:
        n, q, p = l.split(",")
        out += "%s,%s,%s,%d\n" % (n, q, p, int(q) * int(p))
        tot += int(q) * int(p)
    return {"采购/清单.csv": out + "合计,,,%d\n" % tot}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
