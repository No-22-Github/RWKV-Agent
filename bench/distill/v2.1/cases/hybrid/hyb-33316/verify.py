# DISTILL-CANARY-5b39b023 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '64db46d77bda5d12aee7164f6938da113d83bdf2c6c3e494ad0213d25a4975dc', "fixture changed"
def compute(files, web):
    import re
    vs = re.findall(r"- (\d+\.\d+\.\d+) \(", [w for w in web if "tern-build" in w["url"]][0]["content"])
    return {"env/prod.cfg": files["env/prod.cfg"].replace("3.2.0", vs[0]), "env/staging.cfg": files["env/staging.cfg"].replace("3.2.0", vs[1])}, [[vs[0]], [vs[1]]]

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
