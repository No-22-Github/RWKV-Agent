# DISTILL-CANARY-00b53b17 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '78e4dc18f88daa37282e2e84b3e3f960d850c25943af4fe51f2a05089899863c', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["价格/报价.txt"].split("\n")[1:]:
        l = l.strip()
        if not l:
            continue
        p = int(l.rsplit(" ", 1)[1].rstrip("元"))
        if p > 100:
            rows.append("- %s：%d元" % (l.split()[0], p))
    return {"价格/贵重物品.md": "\n".join(rows) + "\n"}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
