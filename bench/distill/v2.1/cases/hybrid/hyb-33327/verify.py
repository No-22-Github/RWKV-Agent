# DISTILL-CANARY-f6bac9b0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '28a572dd30f27a30475dc74c5bd5efb35ffb3aff433d95b5ba3585e52a408250', "fixture changed"
def compute(files, web):
    c = {}
    for l in files["考勤/打卡.csv"].splitlines()[1:]:
        d, n, t = l.split(",")
        if t > "09:10":
            c[n] = c.get(n, 0) + 1
    late = sorted((k for k in c if c[k] >= 3), key=lambda k: (-c[k], k))
    return {"考勤/迟到.txt": "".join("%s=%d\n" % (k, c[k]) for k in late)}, [[late[0]]]

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
