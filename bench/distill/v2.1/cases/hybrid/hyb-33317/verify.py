# DISTILL-CANARY-0e7a9fae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bd9d725b9d2b17166822691a4b2b42cc631451e2864e818cef1a950d7c2fc8fb', "fixture changed"
def compute(files, web):
    from collections import Counter
    c = Counter(l.split(",")[1] for l in files["订单/q3.csv"].splitlines()[1:])
    order = sorted(c, key=lambda k: -c[k])
    return {"订单/城市订单.txt": "".join("%s=%d\n" % (k, c[k]) for k in order)}, [[order[0]]]

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
