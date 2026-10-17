# DISTILL-CANARY-abed21dd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '71a561d588d2d6fc6f00c306092c168df842aede44276d6ef7833946ac72c065', "fixture changed"
def compute(files, web):
    rows = [l.split(",")[1] for l in files["出游/报名.csv"].splitlines()[1:]]
    t = (80 * rows.count("成人") + 40 * rows.count("学生")) * 0.9 if len(rows) >= 10 else 80 * rows.count("成人") + 40 * rows.count("学生")
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
