# DISTILL-CANARY-73cb59c6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0963fe6beb501a83f3b172ca84d47e2036f5a226e5ced386662e521457eba0a5', "fixture changed"
def compute(files, web):
    import re
    n = len(files["学校/学生名单.csv"].splitlines()) - 1
    d = re.search(r"正式上课：(\S+)", web[0]["content"]).group(1)
    return {"学校/日程.md": files["学校/日程.md"] + "- 正式上课：%s\n" % d}, [[str(n), d]]

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
