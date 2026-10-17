# DISTILL-CANARY-9289334c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1584ad6fadbf61aae4c6a00beb99afb750f8ebb66c194b350541ec9ccc77bf57', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "nimbus-cli.dev" in w["url"]][0]["content"]
    v = re.search(r"稳定版：(\d+\.\d+\.\d+)", pg).group(1)
    return {"deploy/versions.env": files["deploy/versions.env"].replace("NIMBUS_VERSION=4.9.0", "NIMBUS_VERSION=" + v)}, [[v]]

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
