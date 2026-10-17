# DISTILL-CANARY-b1afedfc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '209c291362bd4b96695d616d99285a245543bbceebf75fde4b8ba6090eafc748', "fixture changed"
def compute(files, web):
    import re
    n = sum(1 for l in files["笔记/待办.md"].splitlines() if l.startswith("- [ ]"))
    v = re.search(r"当前版本：(\S+?)（", [w for w in web if "quartznotes" in w["url"]][0]["content"]).group(1)
    return {}, [[str(n), v]]

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
