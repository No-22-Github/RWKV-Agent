# DISTILL-CANARY-e3a7340f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '710115c82c2deff238314bfb2de98c27eb855b7ff9cd01ef4ed4656fed6a4cef', "fixture changed"
def compute(files, web):
    t = 0
    for l in files["销售/明细.csv"].splitlines()[1:]:
        a = l.split(",")
        t += int(a[1]) * int(a[2])
    s = ["{:,}".format(t), str(t)]
    return {"销售/合计.txt": "合计=%d\n" % t}, [s]

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
