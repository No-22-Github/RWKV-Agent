# DISTILL-CANARY-76a77975 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'be855769c3045e612ea41b33c94a0ca11f589ec9fc12680781fa5693e86479e3', "fixture changed"
def compute(files):
    d = {}
    for l in files["公告/周报.md"].split("\n"):
        if "：" in l:
            k, v = l.split("：", 1)
            d[k] = v
    out = "## 本周完成\n"
    out += "".join("- %s\n" % x for x in d["本周完成"].rstrip("。").split("、"))
    out += "\n## 下周计划\n" + "".join("- %s\n" % x for x in d["下周计划"].rstrip("。").split("、"))
    out += "\n## 风险\n- %s\n" % d["风险"].rstrip("。")
    return {"公告/周报_条目.md": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
