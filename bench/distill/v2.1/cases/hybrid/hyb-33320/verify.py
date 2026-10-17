# DISTILL-CANARY-c634fee2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '10641615832ebd4ee8c137b7322d246fd2cc33622d26da28e9d2fa5f4c0377df', "fixture changed"
def compute(files, web):
    t = {}
    for l in files["time/sheet.csv"].splitlines()[1:]:
        d, p, h = l.split(",")
        t[p] = t.get(p, 0) + int(h)
    top = max(t, key=lambda k: t[k])
    return {"time/top.txt": "%s,%d\n" % (top, t[top])}, [[top]]

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
