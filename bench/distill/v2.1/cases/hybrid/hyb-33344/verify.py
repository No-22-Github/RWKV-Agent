# DISTILL-CANARY-58a76e5f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '34594746901b0adff581de67f58a7be97caa5dc082385cfaf0f72e153064c154', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "pinecrestpost" in w["url"]][0]["content"]
    d = [float(x) for x in re.search(r"Domestic letter \(up to 1 oz\): \$([\d.]+), each additional ounce \$([\d.]+)", pg).groups()]
    i = [float(x) for x in re.search(r"International letter \(up to 1 oz\): \$([\d.]+), each additional ounce \$([\d.]+)", pg).groups()]

    def cost(t, rate):
        return sum(rate[0] + rate[1] * (int(l.split()[0]) - 1) for l in t.splitlines())
    out = []
    for v in (cost(files["office/domestic.txt"], d), cost(files["office/international.txt"], i)):
        v = round(v, 2)
        out.append(list(dict.fromkeys(["%.2f" % v, ("%.2f" % v).rstrip("0").rstrip("."), "{:,.2f}".format(v)])))
    return {}, out

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
