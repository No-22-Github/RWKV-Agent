# DISTILL-CANARY-7696df74 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'de00df8df61ef9a242c1e6747e152abfbbb6bc8699ddcf675706d959230b25aa', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "zephyrfreight" in w["url"]][0]["content"]
    rt = {z: float(p) for z, p in re.findall(r"Zone (\w): \$([\d.]+) per kg", pg)}
    t = round(sum(int(l.split(",")[1]) * rt[l.split(",")[2]] for l in files["shipping/parcels.csv"].splitlines()[1:]), 2)
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
