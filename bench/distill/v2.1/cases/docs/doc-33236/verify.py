# DISTILL-CANARY-0f62c593 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'da4060cf49546f7da05f86a53d6c8e71597d6bec7eeaf484216d327c157e02a7', "fixture changed"
files = case["files"]
def compute(files):
    d = {}
    for l in files["值班/排班.txt"].strip().split("\n"):
        day, n = l.split(" ")
        d.setdefault(n, []).append(day)
    names = sorted(d, key=lambda n: (-len(d[n]), n))
    return {"值班/按人.md": "".join("%s（%d次）：%s\n" % (n, len(d[n]), "、".join(d[n])) for n in names)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
