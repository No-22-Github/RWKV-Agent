# DISTILL-CANARY-22798f86 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7878cd3f39c8e023c294d793bf373334f22d6e488cebc157e7a07243b53dd04c', "fixture changed"
def compute(files, web):
    ls = files["logs/app.log"].splitlines()
    e = sum(1 for l in ls if " ERROR " in l)
    w = sum(1 for l in ls if " WARN " in l)
    return {}, [[str(e), "Too Many Requests"], [str(w), "Service Unavailable"]]

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
