# DISTILL-CANARY-b351935e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9895f7e0b94ab1d4b98eec79b447e69d55208ed497b6554014ddb794cfd2a036', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "lumencloud" in w["url"]][0]["content"]
    h = re.search(r"\| eu-north \| (\S+) \|", pg).group(1)
    return {".env.example": files[".env.example"].replace("api.eun1.lumencloud.dev", h)}, [[h]]

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
