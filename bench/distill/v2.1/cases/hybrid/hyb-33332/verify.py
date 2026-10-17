# DISTILL-CANARY-622e062c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c443a779d1f53a046e52bad0d1e26a6f57b225b36b3f2c0ce9365fde05e4938f', "fixture changed"
def compute(files, web):
    seen, c = set(), {}
    for l in files["qa/inspections.csv"].splitlines()[1:]:
        i, ln, res = l.split(",")
        if i in seen:
            continue
        seen.add(i)
        if res == "defect":
            c[ln] = c.get(ln, 0) + 1
    return {"qa/defects.txt": "".join("%s=%d\n" % (k, c.get(k, 0)) for k in ("L1", "L2", "L3", "L4")) + "total=%d\n" % sum(c.values())}, [[str(sum(c.values()))]]

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
