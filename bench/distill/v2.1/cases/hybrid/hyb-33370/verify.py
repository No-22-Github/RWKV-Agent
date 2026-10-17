# DISTILL-CANARY-53200afc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3400ef49e7562b653be0ce299b6d0b23320213de9faba04e2e3220c6e729ba36', "fixture changed"
def compute(files, web):
    f = lambda p: sum(int(l.split(",")[1]) for l in files[p].splitlines()[1:])
    a, b = f("财务/sales.csv"), f("财务/refunds.csv")
    return {}, [list(dict.fromkeys([str(a), "{:,}".format(a)])), list(dict.fromkeys([str(b), "{:,}".format(b)])), list(dict.fromkeys([str(a - b), "{:,}".format(a - b)]))]

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
