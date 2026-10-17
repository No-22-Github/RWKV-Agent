# DISTILL-CANARY-b4afe54a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a5ec931ba9bc88ab6125a6ded4023ec702f918abf6163019011fc1156be5d8fc', "fixture changed"
files = case["files"]
def compute(files):
    d, order = {}, []
    for l in files["食谱/周计划.md"].split("\n"):
        if l.startswith("- "):
            n, q = l[2:].split(" ")
            num = int("".join(c for c in q if c.isdigit()))
            unit = "".join(c for c in q if not c.isdigit())
            if n not in d:
                order.append(n)
                d[n] = [0, unit]
            d[n][0] += num
    return {"食谱/购物清单.md": "".join("- %s %d%s\n" % (n, d[n][0], d[n][1]) for n in order)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
