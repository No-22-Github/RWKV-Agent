# DISTILL-CANARY-a9ada598 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '71608c9fb080c326b81b0b057a7621298aea6f798ebc767da60ccac46e8a299f', "fixture changed"
def compute(files, web):
    import re
    n = {"500": 0, "502": 0, "503": 0}
    for l in files["logs/access.log"].splitlines():
        m = re.search(r'" (\d{3}) \d+$', l)
        if m and m.group(1) in n:
            n[m.group(1)] += 1
    return {"logs/errors.txt": "".join("%s=%d\n" % (k, n[k]) for k in ("500", "502", "503"))}, [[str(n["500"])]]

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
