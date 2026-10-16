# DISTILL-CANARY-44c23d12 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7327f567061aecd3f25a77254cd267d3e1f99557328f798fbe077a0ce132dc6d', "fixture changed"
def compute(files):
    out = "| 编码 | 名称 | 库存 |\n| ---: | :--- | ---: |\n"
    for l in files["商品/库存.csv"].strip().split("\n")[1:]:
        c, n, s = l.split(",")
        out += "| %s | %s | %s |\n" % (c.zfill(5), n, s)
    return {"商品/库存.md": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
