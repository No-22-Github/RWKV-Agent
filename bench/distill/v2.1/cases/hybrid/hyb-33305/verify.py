# DISTILL-CANARY-bacb4799 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '43dc86fb1f8211996454a9f82af53659159640cb472316d73a74bff86237199d', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "forge-lang" in w["url"]][0]["content"]
    v = re.search(r"Stable: (\d+\.\d+\.\d+)", pg).group(1)
    return {"rust-toolchain.toml": files["rust-toolchain.toml"].replace("1.78.0", v),
            "Dockerfile": files["Dockerfile"].replace("rust:1.78.0", "rust:" + v)}, [[v], [v]]

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
