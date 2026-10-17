# DISTILL-CANARY-64c8c9b0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f05af510942a7aa5c7a2bd2d41c792d7cb11d791fa360cc5a3c563f87b81c107', "fixture changed"
def compute(files, web):
    import re
    loc = re.search(r"## (\d+\.\d+\.\d+)", files["CHANGELOG.md"]).group(1)
    new = re.search(r"当前稳定版：(\S+)", [w for w in web if "ledgerly" in w["url"]][0]["content"]).group(1)
    return {"升级提示.txt": "本地=%s\n最新=%s\n" % (loc, new)}, [[loc, new]]

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
