# DISTILL-CANARY-8da457e8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aedcb33da450ce807a3e3d9ccbd9b22edb1db38f1ae38c2b1b503251ae5b5999', "fixture changed"
def compute(files):
    ls = [l.split(" ", 1) for l in files["日报/原始.txt"].strip().split("\n")]
    keep = [l for l in ls if l[0] != "09-14"]
    return {"日报/汇报.md": "# 汇报\n\n" + "".join("- %s：%s\n" % (a, b) for a, b in keep)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
