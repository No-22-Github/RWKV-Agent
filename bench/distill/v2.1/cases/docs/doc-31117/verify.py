# DISTILL-CANARY-4db12acd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c7822873100be3ea71db572472b2830939be1538e120357882bc7808a9f7ae18', "fixture changed"
def compute(files):
    out = []
    for l in files["readme/版本.md"].split("\n"):
        if l.startswith("## "):
            out.append(l[3:] + "：")
            n = 0
        elif l.startswith("- "):
            n += 1
            out[-1] = out[-1].split("：")[0] + "：%d 项" % n
    return {"readme/版本统计.txt": "".join(o + "\n" for o in out)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
