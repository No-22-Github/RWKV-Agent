# DISTILL-CANARY-7ff16f0a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cca611b5b7c822b4f1ac5b342edb495d175e7b9a70690cd831cb937a68ce6c6f', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "tietayun" in w["url"]][0]["content"]
    p = re.search(r"标准存储：([\d.]+)", pg).group(1)
    return {"budget/storage.json": files["budget/storage.json"].replace('"price_per_gb_month": 0.15', '"price_per_gb_month": ' + p)}, [[p]]

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
