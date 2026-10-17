# DISTILL-CANARY-0e636c56 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52ccc5b9da27ba8b9aa854acb30a2f2438fb6c36dc4b9afedb283b47c6bdd0aa', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "northgrid" in w["url"]][0]["content"]
    p, n, g = [float(re.search(k + r"：([\d.]+) 元/度", pg).group(1)) for k in ("峰时", "平时", "谷时")]
    rows = [list(map(int, l.split(",")[1:])) for l in files["车间/9月用电.csv"].splitlines()[1:]]
    t = round(sum(a * p + b * n + c * g for a, b, c in rows), 2)
    return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t), "{:,.0f}".format(t)]))]

FINAL, ANS = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    assert set(a) <= set(e.get("output_contains", [])) | set(e.get("output_contains_any", [])), a
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}, "answers": ANS}, ensure_ascii=False))
