# DISTILL-CANARY-ef6b7d85 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0de28e8ac1ff6d4ea382f86f434ab15db7ca965cabb90ef57798695379f6cd56', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if w["url"].endswith("/download")][0]["content"]
    v = re.search(r"Current release: (\S+)", pg).group(1)
    return {"scripts/install.sh": files["scripts/install.sh"].replace("VERSION=2.5.0", "VERSION=" + v)}, [[v]]

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
