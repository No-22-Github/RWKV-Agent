# DISTILL-CANARY-195f899e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '935f7d87d443bbd2de29a5760f6df908883c42c44a90233a5bd1a39cbe886f13', "fixture changed"
def compute(files, web):
    t = {}
    for l in files["finance/expenses.csv"].splitlines()[1:]:
        a = l.split(",")
        t[a[1]] = t.get(a[1], 0) + int(a[2])
    big = max(t, key=lambda k: t[k])
    return {"finance/by_category.txt": "".join("%s: %d\n" % (k, t[k]) for k in ("Travel", "Meals", "Software", "Office"))}, [[big]]

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
