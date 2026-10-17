# DISTILL-CANARY-f3ca4c98 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd86081e563328abe9ffc53cf4a430986e12bdabd6d4491bef647d31761e33590', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "qinglan-home" in w["url"]][0]["content"]
    tel = re.search(r"启用）：(\S+)", pg).group(1)
    mail = re.search(r"服务邮箱：(\S+)", pg).group(1)
    return {"docs/联系我们.md": files["docs/联系我们.md"].replace("400-620-1180", tel),
            "docs/FAQ.md": files["docs/FAQ.md"].replace("help@qinglan-home.com", mail)}, [[tel], [mail]]

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
