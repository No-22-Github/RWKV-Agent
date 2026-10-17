# DISTILL-CANARY-ac087469 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8389bce19154eb764f6733f4adf39a41b46a4e281dfeb52019f676b37b34e0c5', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "harborpay" in w["url"]][0]["content"]
    u = re.search(r"生产环境基础地址：(\S+)", pg).group(1)
    return {"config/payment.yaml": files["config/payment.yaml"].replace("https://gateway.harborpay.io/v2", u)}, [[u]]

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
