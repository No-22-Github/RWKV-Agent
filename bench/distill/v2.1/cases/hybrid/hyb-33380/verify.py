# DISTILL-CANARY-da12ca3b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '411fbad8dedc00034e017d8931417dbd08ebfc42160e7acd484a586354c2b136', "fixture changed"
def compute(files, web):
    f = lambda p: sum(int(l.split(",")[1]) for l in files[p].splitlines()[1:])
    x, y = f("账本/餐饮.csv"), f("账本/交通.csv")
    return {}, [list(dict.fromkeys([str(x), "{:,}".format(x)])), list(dict.fromkeys([str(x + y), "{:,}".format(x + y)]))]

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
