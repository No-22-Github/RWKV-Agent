# DISTILL-CANARY-01dea433 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ea19a05503b95e4dc0f719f2836684f4522e37fdce764177d01cdcede6b946da', "fixture changed"
def compute(files, web):
    c = {}
    for l in files["cron/history.log"].splitlines():
        d, j, s = l.split()
        if s == "FAILED":
            c[j] = c.get(j, 0) + 1
    top = sorted(c, key=lambda k: (-c[k], k))[:3]
    return {"cron/worst.txt": "".join("%s %d\n" % (k, c[k]) for k in top)}, [[top[0]]]

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
