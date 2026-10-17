# DISTILL-CANARY-e5ed691c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c5c8a5221ec7786f32729f08b80624e50da47515c53f7dc7c68b3550b0f75ae3', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "fennelhq" in w["url"]][0]["content"]
    pr = dict(re.findall(r"(\w+): \$(\d+) per user", pg))
    n = sum(1 for l in files["notes/todo.md"].splitlines() if l.startswith("- [ ]"))
    t = files["notes/todo.md"].replace("- [ ] renew passport", "- [x] renew passport")
    return {"notes/todo.md": t}, [[str(n), pr["Starter"]], [pr["Team"]]]

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
