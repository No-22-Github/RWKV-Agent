# DISTILL-CANARY-096d331d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '506187ad56c27b64a3686447df2d3c794834ab0c87b9e89c9e43a3428126ee12', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "oriental-trade" in w["url"]][0]["content"]
    tgt = {k: int(v) for k, v in re.findall(r"(华.)：(\d+) 万元", pg)}
    s = {}
    for l in files["销售/q3.csv"].splitlines()[1:]:
        a = l.split(",")
        s[a[0]] = s.get(a[0], 0) + int(a[2])
    return {}, [[str(s["华东"]), str(tgt["华东"])], [str(s["华南"]), str(int(round(s["华南"] * 100.0 / tgt["华南"])))]]

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
