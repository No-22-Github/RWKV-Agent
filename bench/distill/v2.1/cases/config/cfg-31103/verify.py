# DISTILL-CANARY-12d96743 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'effe8c7bf11ce188231d9511bfb11c059b94383ab074319d7b030207dd361820', "fixture changed"
def compute(files):
    def parse(t):
        return dict(l.split("=", 1) for l in t.strip().split("\n"))
    a, b = parse(files["配置/dev.env"]), parse(files["配置/prod.env"])
    keys = sorted(set(a) | set(b))
    out = "| 键 | dev | prod |\n|---|---|---|\n"
    for k in keys:
        out += "| %s | %s | %s |\n" % (k, a.get(k, "-"), b.get(k, "-"))
    return {"配置/对比.md": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
