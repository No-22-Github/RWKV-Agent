# DISTILL-CANARY-3ff347c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bc2f41db7ee041ebc539d4185756702742d8f4ce2b8fe0b2d603cd54f9219723', "fixture changed"
def compute(files, web):
    c = {}
    for l in files["工单/本月.csv"].splitlines()[1:]:
        t, o, s = l.split(",")
        if s != "已关闭":
            c[o] = c.get(o, 0) + 1
    t = sorted(c, key=lambda k: (-c[k], k))
    return {"工单/未关闭.txt": "".join("%s=%d\n" % (k, c[k]) for k in t)}, [[t[0]]]

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
