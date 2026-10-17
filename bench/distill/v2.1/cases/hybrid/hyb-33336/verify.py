# DISTILL-CANARY-70ccd067 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4a8fa8b5c8598f1393bdf4e28488a25f960f5c0c36ef08121b10cdd91f478ed8', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "vortexcompute.io" in w["url"]][0]["content"]
    pr = dict(re.findall(r"- (vx\.\w+): \$([\d.]+) / hour", pg))
    t = round(sum(int(l.split(",")[1]) * float(pr[l.split(",")[0]]) for l in files["cloud/usage.csv"].splitlines()[1:]), 2)
    return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t)]))]

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
