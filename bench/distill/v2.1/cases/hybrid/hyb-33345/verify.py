# DISTILL-CANARY-bf63e511 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '16771294b95c94b23abc3ea4256b3818db40e9cfa769090cbd9ac7b2b21f4003', "fixture changed"
def compute(files, web):
    import math
    out = []
    tot = 0
    for l in files["发货/货物.csv"].splitlines()[1:]:
        n, w, a, b, c = l.split(",")
        kg = math.ceil(max(float(w), int(a) * int(b) * int(c) / 6000.0) - 1e-9)
        out.append(kg * 8)
    return {}, [[str(out[0])], [str(sum(out))]]

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
