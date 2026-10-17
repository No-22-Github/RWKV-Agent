# DISTILL-CANARY-30ce3c5b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd82d8d3d5583bcd4b2b8e6c3276c23c67621054ce4ab1f7a0c2eefbdd6cfffd7', "fixture changed"
def compute(files, web):
    c = {}
    for l in files["audit/files.csv"].splitlines()[1:]:
        p, s = l.split(",")
        e = p.rsplit(".", 1)[1]
        c[e] = c.get(e, 0) + int(s)
    t = sorted(c, key=lambda k: (-c[k], k))
    return {"audit/by_ext.txt": "".join(".%s=%d\n" % (k, c[k]) for k in t)}, [[".%s=%d" % (t[0], c[t[0]])]]

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
