# DISTILL-CANARY-3b573e29 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '39f59f87a53fcd9b65080fe0df84eca74c6ae41cdf30adc718e4d65462a49050', "fixture changed"
def compute(files, web):
    d = {}
    for l in files["教务/期中.csv"].splitlines()[1:]:
        n, c, s = l.split(",")
        d.setdefault(c, []).append(int(s))
    return {"教务/班级统计.txt": "".join("%s,%d,%d\n" % (c, len(d[c]), max(d[c])) for c in ("一班", "二班", "三班"))}, [["%s,%d,%d" % ("一班", len(d["一班"]), max(d["一班"]))]]

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
