# DISTILL-CANARY-084eefe6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5a0cc231f1dd1ec12cd76e9af2ed96910163c0cadb4d802d6a9b1fc91d1edd60', "fixture changed"
files = case["files"]
def compute(files):
    qs = [l[3:] for l in files["帮助/常见问题.md"].split("\n") if l.startswith("## ")]
    return {"帮助/问题目录.md": "".join("%d. %s\n" % (i + 1, q) for i, q in enumerate(qs))}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
