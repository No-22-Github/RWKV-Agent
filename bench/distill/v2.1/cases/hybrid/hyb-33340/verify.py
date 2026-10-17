# DISTILL-CANARY-f59876e0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3a3bcaee439530600fd158872f7f1af43eb77a460f0f7fd38c134e4cceb9b998', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "lattice-ai" in w["url"]][0]["content"]
    pr = {m: (float(a), float(b)) for m, a, b in re.findall(r"(lattice-\w+): input \$([\d.]+) / 1M tokens, output \$([\d.]+)", pg)}
    t = 0.0
    for l in files["ml/usage.csv"].splitlines()[1:]:
        d, m, i, o = l.split(",")
        t += int(i) / 1e6 * pr[m][0] + int(o) / 1e6 * pr[m][1]
    t = round(t, 2)
    return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip(".")]))]

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
