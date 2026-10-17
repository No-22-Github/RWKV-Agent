# DISTILL-CANARY-53be2087 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '860576de096a8e4b2c9caaf82b05d5afc011a9532ce4a67457c430c83d2912d1', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "xinghe-edu.cn/notice" in w["url"]][0]["content"]
    u = re.search(r"报名网址已更换为：(\S+)", pg).group(1)
    d = re.search(r"报名截止日期：(\S+)", pg).group(1)
    t = files["公告/报名说明.md"].replace("https://www.xinghe-edu.cn/apply", u).replace("2026年9月30日", d)
    return {"公告/报名说明.md": t}, [[u, d]]

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
